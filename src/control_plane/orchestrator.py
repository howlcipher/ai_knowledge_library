#!/usr/bin/env python3
"""
orchestrator.py

Closed-loop AI Engineering Control Plane orchestrator.
Enforces the complete governed lifecycle:
Discovery -> Shadow Audit -> Plan/Route -> Implement -> Delta Capture ->
Adversarial Review -> Structured Validation -> Reconciliation ->
Remediation Loop -> Targeted Re-review -> Deterministic Verification ->
Human Authority Boundary Gate -> Complete Evidence Ledger.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json, os, shutil, sys, time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import yaml

from src.control_plane.agent_execution import AgentBackend, AgentBackendRegistry, AgentExecutionResult, AgentUnavailableError
from src.control_plane.evidence_ledger import EvidenceEntry, EvidenceLedger
from src.control_plane.git_baseline import GitBaseline, RepositoryDelta, capture_baseline, capture_delta
from src.control_plane.howlframe_runner import HowlFrameAuditRunner, get_dogfood_mode, DEFAULT_INSTRUCTION_BUDGET
from src.control_plane.human_boundary import HumanBoundaryGate, BoundaryCheckResult, HumanDecisionPacket
from src.control_plane.project_adapter import ProjectAdapter, ProjectContext
from src.control_plane.reconciliation import ReviewFinding, ReconciliationResult, ReviewReconciler
from src.control_plane.review_runner import ReviewRunner, ReviewCycleResult, SingleReviewResult
from src.control_plane.reviewers import get_reviewer_role
from src.control_plane.router import TaskRouter, RoutingDecision
from src.control_plane.task_spec import TaskSpec
from src.control_plane.verification import VerificationPlan, VerificationStep

ORCHESTRATOR_SCHEMA_VERSION = "howlplane.orchestrator/v1"


@dataclass
class OrchestrationConfig:
    """Runtime configuration for governed task orchestration."""

    max_remediation_cycles: int = 3
    max_review_cycles: int = 4
    timeout_seconds: int = 600
    dogfood_mode: str = "shadow"
    enable_howlframe_audit: bool = True
    record_evidence: bool = True
    stop_on_verification_failure: bool = True
    force: bool = False
    skip_doctor: bool = False
    custom_backend: Optional[AgentBackend] = None
    custom_reviewer_fn: Optional[Callable[[str, str, TaskSpec], str]] = None
    custom_remediation_fn: Optional[Callable[[TaskSpec, Path, List[ReviewFinding]], None]] = None
    reviewer_agent_mapping: Optional[Dict[str, str]] = None


@dataclass
class OrchestrationResult:
    """Complete result packet from governed task execution."""

    task_id: str
    task_spec: TaskSpec
    final_state: str  # "complete", "awaiting_human", "failed", "blocked"
    exit_code: int
    routing_decision: Optional[RoutingDecision] = None
    initial_delta: Optional[RepositoryDelta] = None
    final_delta: Optional[RepositoryDelta] = None
    review_cycles: List[ReviewCycleResult] = field(default_factory=list)
    reconciliation: Optional[ReconciliationResult] = None
    verification_plan: Optional[VerificationPlan] = None
    boundary_result: Optional[BoundaryCheckResult] = None
    howlframe_audit_status: Optional[str] = None
    howlframe_audit_match: bool = True
    remediation_cycles_count: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    run_dir: Optional[str] = None
    schema: str = ORCHESTRATOR_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "final_state": self.final_state,
            "exit_code": self.exit_code,
            "routing_decision": asdict(self.routing_decision) if self.routing_decision else None,
            "initial_delta": self.initial_delta.to_dict() if self.initial_delta else None,
            "final_delta": self.final_delta.to_dict() if self.final_delta else None,
            "review_cycles": [c.to_dict() for c in self.review_cycles],
            "reconciliation": self.reconciliation.to_dict() if self.reconciliation else None,
            "verification_plan": self.verification_plan.to_dict() if self.verification_plan else None,
            "howlframe_audit_status": self.howlframe_audit_status,
            "howlframe_audit_match": self.howlframe_audit_match,
            "remediation_cycles_count": self.remediation_cycles_count,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "run_dir": self.run_dir,
            "schema": self.schema,
        }


class GovernedTaskOrchestrator:
    """
    Drives the end-to-end governed engineering lifecycle, maintaining
    strict control over state transitions, adversarial reviews,
    remediation loops, verification gates, and human authority boundaries.
    """

    def __init__(
        self,
        target_repo: Union[str, Path],
        control_plane_root: Optional[Union[str, Path]] = None,
        config: Optional[OrchestrationConfig] = None,
    ):
        self.target_repo = Path(target_repo).resolve()
        self.control_plane_root = (
            Path(control_plane_root).resolve()
            if control_plane_root
            else Path(__file__).resolve().parents[2]
        )
        self.config = config or OrchestrationConfig()
        ledger_path = str(self.control_plane_root / "logs" / "control_plane" / "evidence_ledger.jsonl")
        self.ledger = EvidenceLedger(ledger_path)

    def _record_event(
        self,
        task_id: str,
        agent_id: str,
        action: str,
        command: Optional[str] = None,
        result: Optional[str] = None,
        artifact: Optional[str] = None,
        spec: Optional[TaskSpec] = None,
        findings_summary: Optional[Dict[str, int]] = None,
        verification_summary: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Records an immutable event in the append-only evidence ledger."""
        if not self.config.record_evidence:
            return

        meta = metadata or {}
        entry = EvidenceEntry(
            task_id=task_id,
            agent_id=agent_id,
            action=action,
            command=command,
            result=result,
            artifact=artifact,
            task_class=spec.task_class if spec else None,
            risk_level=spec.risk_level if spec else None,
            reasoning_tier=spec.recommended_reasoning_tier if spec else None,
            actual_agent=agent_id,
            repository=self.target_repo.name,
            findings_summary=findings_summary,
            verification_summary=verification_summary,
            metadata=meta,
        )
        try:
            self.ledger.append_entry(entry)
        except Exception:
            pass

    def prepare_task_plan(
        self,
        task_spec: TaskSpec,
        planned_actions: Optional[List[str]] = None,
    ) -> Tuple[ProjectContext, RoutingDecision, VerificationPlan, Path, Optional[Any]]:
        """Prepares task run directory, project discovery, routing, verification plan, and review briefs."""
        run_dir = self.target_repo / ".task_runs" / task_spec.task_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "reviews").mkdir(parents=True, exist_ok=True)
        (run_dir / "remediation").mkdir(parents=True, exist_ok=True)

        ctx = ProjectAdapter.discover(self.target_repo)
        (run_dir / "project_context.json").write_text(ctx.to_json(), encoding="utf-8")

        router = TaskRouter()
        routing = router.route(task_spec)
        (run_dir / "route.json").write_text(json.dumps(asdict(routing), indent=2), encoding="utf-8")

        verif_plan = ProjectAdapter.create_verification_plan(ctx, task_id=task_spec.task_id)
        (run_dir / "verification_plan.json").write_text(verif_plan.to_json(), encoding="utf-8")

        task_spec.recommended_agent = routing.selected_agent_id
        task_spec.actual_agent = routing.selected_agent_id
        task_spec.is_override = routing.is_override
        task_spec.override_reason = routing.rationale if routing.is_override else None
        if task_spec.current_state == "discovered":
            task_spec.transition_to("planned", "Task routed and verification plan generated")
        task_spec.save_to_file(str(run_dir / "task.yaml"))

        for role_id in routing.recommended_reviewers:
            role = get_reviewer_role(role_id)
            if role:
                (run_dir / "reviews" / f"{role_id}.md").write_text(
                    role.render_brief(task=task_spec, diff_content=""), encoding="utf-8"
                )
        (run_dir / "findings_template.yaml").write_text("# Review Findings Template\nfindings: []\n", encoding="utf-8")

        hf_res = None
        if self.config.enable_howlframe_audit:
            try:
                hf_res = HowlFrameAuditRunner.run_audit(
                    context=ctx,
                    record_evidence=self.config.record_evidence,
                    task_id=task_spec.task_id,
                    ledger=self.ledger,
                    dogfood_mode="shadow",
                )
                (run_dir / "howlframe_audit.json").write_text(json.dumps(hf_res.to_dict(), indent=2), encoding="utf-8")
            except Exception:
                pass

        return ctx, routing, verif_plan, run_dir, hf_res

    def run(
        self,
        task_spec: TaskSpec,
        planned_actions: Optional[List[str]] = None,
    ) -> OrchestrationResult:
        """
        Executes the complete governed control-plane loop for the task.
        """
        start_time = time.time()
        ctx, routing, verif_plan, run_dir, hf_res = self.prepare_task_plan(task_spec, planned_actions)
        reviews_dir = run_dir / "reviews"
        remediation_base_dir = run_dir / "remediation"
        hf_audit_status = hf_res.status if hf_res else None
        hf_audit_match = (hf_res.status == "MATCH") if hf_res else True

        self._record_event(
            task_id=task_spec.task_id,
            agent_id="control_plane",
            action="task_created",
            spec=task_spec,
            metadata={"repo_path": str(self.target_repo), "project_types": ctx.project_types},
        )
        self._record_event(
            task_id=task_spec.task_id,
            agent_id="control_plane",
            action="project_discovered",
            spec=task_spec,
            metadata={"hygiene_status": ctx.hygiene_status, "has_agents_md": ctx.has_agents_md},
        )
        self._record_event(
            task_id=task_spec.task_id,
            agent_id=routing.selected_agent_id,
            action="route_selected",
            spec=task_spec,
            metadata={
                "selected_agent": routing.selected_agent_id,
                "reviewers": routing.recommended_reviewers,
                "is_override": routing.is_override,
            },
        )

        # --------------------------------------------------------------------
        # Stage 3: Baseline Capture
        # --------------------------------------------------------------------
        baseline = capture_baseline(self.target_repo)
        (run_dir / "baseline.json").write_text(baseline.to_json(), encoding="utf-8")

        # --------------------------------------------------------------------
        # Stage 4: Implementation (implementing)
        # --------------------------------------------------------------------
        task_spec.transition_to("implementing", f"Launching implementation agent: {routing.selected_agent_id}")
        task_spec.save_to_file(str(run_dir / "task.yaml"))

        self._record_event(
            task_id=task_spec.task_id,
            agent_id=routing.selected_agent_id,
            action="implementation_started",
            spec=task_spec,
        )

        # Select backend for implementation
        impl_backend = self.config.custom_backend or AgentBackendRegistry.get_backend(routing.selected_agent_id)
        if not impl_backend.is_available() and not self.config.custom_backend:
            err_msg = f"Selected agent '{routing.selected_agent_id}' is not installed or available on PATH."
            task_spec.transition_to("failed", err_msg)
            task_spec.save_to_file(str(run_dir / "task.yaml"))
            self._record_event(
                task_id=task_spec.task_id,
                agent_id=routing.selected_agent_id,
                action="task_failed",
                result=err_msg,
                spec=task_spec,
            )
            return OrchestrationResult(
                task_id=task_spec.task_id,
                task_spec=task_spec,
                final_state="failed",
                exit_code=1,
                routing_decision=routing,
                howlframe_audit_status=hf_audit_status,
                howlframe_audit_match=hf_audit_match,
                duration_seconds=round(time.time() - start_time, 3),
                error_message=err_msg,
                run_dir=str(run_dir),
            )

        impl_res = impl_backend.execute(
            task=task_spec,
            cwd=self.target_repo,
            role="implementation",
            timeout_seconds=self.config.timeout_seconds,
        )

        impl_dir = run_dir / "implementation"
        impl_dir.mkdir(parents=True, exist_ok=True)
        (impl_dir / "result.json").write_text(impl_res.to_json(), encoding="utf-8")

        if not impl_res.success:
            err_msg = (
                impl_res.stderr.strip()
                if impl_res.stderr and impl_res.stderr.strip()
                else (impl_res.error_message or f"Implementation failed with exit code {impl_res.exit_code}")
            )
            task_spec.transition_to("failed", f"Implementation agent error: {err_msg}")
            task_spec.save_to_file(str(run_dir / "task.yaml"))
            self._record_event(
                task_id=task_spec.task_id,
                agent_id=routing.selected_agent_id,
                action="implementation_completed",
                result="failure",
                spec=task_spec,
                metadata={"exit_code": impl_res.exit_code, "error": err_msg},
            )
            self._record_event(
                task_id=task_spec.task_id,
                agent_id="control_plane",
                action="task_failed",
                result=err_msg,
                spec=task_spec,
            )
            return OrchestrationResult(
                task_id=task_spec.task_id,
                task_spec=task_spec,
                final_state="failed",
                exit_code=impl_res.exit_code if impl_res.exit_code != 0 else 1,
                routing_decision=routing,
                howlframe_audit_status=hf_audit_status,
                howlframe_audit_match=hf_audit_match,
                duration_seconds=round(time.time() - start_time, 3),
                error_message=err_msg,
                run_dir=str(run_dir),
            )

        # Capture actual repository delta attributable to the task
        current_delta = capture_delta(self.target_repo, baseline)
        (impl_dir / "diff.patch").write_text(current_delta.diff_content, encoding="utf-8")
        (run_dir / "diff.patch").write_text(current_delta.diff_content, encoding="utf-8")

        self._record_event(
            task_id=task_spec.task_id,
            agent_id=routing.selected_agent_id,
            action="implementation_completed",
            result="success",
            spec=task_spec,
            metadata={"files_changed": len(current_delta.files_modified) + len(current_delta.files_added)},
        )
        self._record_event(
            task_id=task_spec.task_id,
            agent_id="control_plane",
            action="repository_delta_captured",
            spec=task_spec,
            metadata={
                "files_added": current_delta.files_added,
                "files_modified": current_delta.files_modified,
                "files_deleted": current_delta.files_deleted,
                "insertions": current_delta.insertions,
                "deletions": current_delta.deletions,
            },
        )

        initial_delta = current_delta

        # --------------------------------------------------------------------
        # Stage 5: Independent Adversarial Reviews & Remediation Loop
        # --------------------------------------------------------------------
        task_spec.transition_to("reviewing", "Initiating independent reviewer analysis on actual implementation diff")
        task_spec.save_to_file(str(run_dir / "task.yaml"))

        review_cycles: List[ReviewCycleResult] = []
        latest_reconciliation: Optional[ReconciliationResult] = None
        remediation_count = 0
        current_reviewers = list(routing.recommended_reviewers)

        while True:
            cycle_idx = len(review_cycles) + 1
            self._record_event(
                task_id=task_spec.task_id,
                agent_id="control_plane",
                action="review_started",
                spec=task_spec,
                metadata={"cycle": cycle_idx, "reviewers": current_reviewers},
            )

            cycle_res = ReviewRunner.execute_review_cycle(
                task=task_spec,
                diff_content=current_delta.diff_content,
                reviewer_roles=current_reviewers,
                cwd=self.target_repo,
                backend=self.config.custom_backend,
                cycle_index=cycle_idx,
                reviewer_agent_mapping=self.config.reviewer_agent_mapping,
                custom_reviewer_fn=self.config.custom_reviewer_fn,
            )
            review_cycles.append(cycle_res)
            latest_reconciliation = cycle_res.reconciliation

            # Save review cycle artifacts
            cycle_dir = reviews_dir if cycle_idx == 1 else (remediation_base_dir / f"cycle-{remediation_count:02d}" / "re_review")
            cycle_dir.mkdir(parents=True, exist_ok=True)
            for role_id, single_rev in cycle_res.reviewer_results.items():
                (cycle_dir / f"{role_id}.md").write_text(single_rev.raw_output, encoding="utf-8")
                (cycle_dir / f"{role_id}_findings.yaml").write_text(
                    yaml.dump([f.to_dict() for f in single_rev.findings], sort_keys=False),
                    encoding="utf-8",
                )

            # Persist findings and reconciliation
            findings_data = {"findings": [f.to_dict() for f in cycle_res.all_findings]}
            (run_dir / "findings.yaml").write_text(yaml.dump(findings_data, sort_keys=False), encoding="utf-8")
            if cycle_res.reconciliation:
                (run_dir / "reconciliation.json").write_text(json.dumps(cycle_res.reconciliation.to_dict(), indent=2), encoding="utf-8")
                (run_dir / "reconciliation_report.md").write_text(cycle_res.reconciliation.render_markdown(), encoding="utf-8")

            findings_summary = {
                "total": len(cycle_res.all_findings),
                "blocker": cycle_res.reconciliation.unresolved_blockers if cycle_res.reconciliation else 0,
                "high": cycle_res.reconciliation.unresolved_highs if cycle_res.reconciliation else 0,
            }
            self._record_event(
                task_id=task_spec.task_id,
                agent_id="control_plane",
                action="review_completed",
                spec=task_spec,
                findings_summary=findings_summary,
                metadata={"status": cycle_res.status, "cycle": cycle_idx},
            )

            # Check if any findings require remediation
            if not cycle_res.requires_remediation:
                # Review stage satisfied cleanly
                break

            # If remediation required, check cycle bounds
            if remediation_count >= self.config.max_remediation_cycles:
                err_msg = (
                    f"Remediation limit reached ({self.config.max_remediation_cycles} cycles) with "
                    f"{findings_summary['blocker']} blockers and {findings_summary['high']} high findings remaining."
                )
                task_spec.transition_to("awaiting_human", f"Max remediation cycles exceeded: {err_msg}")
                task_spec.save_to_file(str(run_dir / "task.yaml"))

                # Create human decision packet for unresolved findings
                decision_pkt = HumanDecisionPacket(
                    task_id=task_spec.task_id,
                    objective=task_spec.objective,
                    change_summary=f"Implementation diff ({current_delta.insertions} ins, {current_delta.deletions} del) has unresolved reviewer findings.",
                    boundary_triggers=["security_policy_exception"] if findings_summary["high"] > 0 else ["unresolved_findings"],
                    evidence=[f.title for f in cycle_res.all_findings if f.severity in ("blocker", "high")],
                    risks=["Unresolved reviewer findings may indicate defects or security vulnerabilities."],
                    review_findings_summary=findings_summary,
                    verification_status="unverified",
                    recommended_action="Review finding report in reconciliation_report.md and authorize override or manual remediation.",
                )
                (run_dir / "decision_packet.md").write_text(decision_pkt.render_markdown(), encoding="utf-8")
                self._record_event(
                    task_id=task_spec.task_id,
                    agent_id="control_plane",
                    action="human_boundary_triggered",
                    spec=task_spec,
                    metadata={"reason": err_msg},
                )
                return OrchestrationResult(
                    task_id=task_spec.task_id,
                    task_spec=task_spec,
                    final_state="awaiting_human",
                    exit_code=2,
                    routing_decision=routing,
                    initial_delta=initial_delta,
                    final_delta=current_delta,
                    review_cycles=review_cycles,
                    reconciliation=latest_reconciliation,
                    verification_plan=verif_plan,
                    remediation_cycles_count=remediation_count,
                    duration_seconds=round(time.time() - start_time, 3),
                    error_message=err_msg,
                    run_dir=str(run_dir),
                )

            # Trigger remediation cycle
            remediation_count += 1
            task_spec.transition_to(
                "remediating",
                f"Remediation cycle {remediation_count}: resolving {len(cycle_res.all_findings)} review findings",
            )
            task_spec.save_to_file(str(run_dir / "task.yaml"))

            self._record_event(
                task_id=task_spec.task_id,
                agent_id=routing.selected_agent_id,
                action="remediation_started",
                spec=task_spec,
                metadata={"cycle": remediation_count, "findings_count": len(cycle_res.all_findings)},
            )

            # Execute remediation
            rem_cycle_dir = remediation_base_dir / f"cycle-{remediation_count:02d}"
            rem_cycle_dir.mkdir(parents=True, exist_ok=True)

            if self.config.custom_remediation_fn:
                self.config.custom_remediation_fn(task_spec, self.target_repo, cycle_res.all_findings)
            else:
                rem_prompt = self._build_remediation_prompt(task_spec, current_delta.diff_content, cycle_res.all_findings)
                rem_res = impl_backend.execute(
                    task=task_spec,
                    cwd=self.target_repo,
                    role="remediation",
                    prompt_override=rem_prompt,
                    timeout_seconds=self.config.timeout_seconds,
                )
                (rem_cycle_dir / "result.json").write_text(rem_res.to_json(), encoding="utf-8")

            # Capture updated repository delta
            current_delta = capture_delta(self.target_repo, baseline)
            (rem_cycle_dir / "diff.patch").write_text(current_delta.diff_content, encoding="utf-8")
            (run_dir / "diff.patch").write_text(current_delta.diff_content, encoding="utf-8")

            self._record_event(
                task_id=task_spec.task_id,
                agent_id=routing.selected_agent_id,
                action="remediation_completed",
                spec=task_spec,
                metadata={"cycle": remediation_count, "files_modified": len(current_delta.files_modified)},
            )
            self._record_event(
                task_id=task_spec.task_id,
                agent_id="control_plane",
                action="repository_delta_captured",
                spec=task_spec,
            )

            # Determine targeted re-reviewers
            current_reviewers = ReviewRunner.determine_re_review_roles(
                cycle_res.all_findings,
                routing.recommended_reviewers,
            )
            task_spec.transition_to("reviewing", f"Re-review cycle {remediation_count + 1} for targeted roles: {current_reviewers}")
            task_spec.save_to_file(str(run_dir / "task.yaml"))

        # --------------------------------------------------------------------
        # Stage 6: Deterministic Verification Gate (verifying)
        # --------------------------------------------------------------------
        task_spec.transition_to("verifying", "Executing deterministic verification plan")
        task_spec.save_to_file(str(run_dir / "task.yaml"))

        self._record_event(
            task_id=task_spec.task_id,
            agent_id="control_plane",
            action="verification_started",
            spec=task_spec,
            metadata={"steps_count": len(verif_plan.steps)},
        )

        verif_status = verif_plan.execute_all(
            cwd=str(self.target_repo),
            stop_on_failure=self.config.stop_on_verification_failure,
        )
        (run_dir / "verification_result.json").write_text(verif_plan.to_json(), encoding="utf-8")

        verif_summary = {s.name: s.status for s in verif_plan.steps}
        self._record_event(
            task_id=task_spec.task_id,
            agent_id="control_plane",
            action="verification_completed",
            spec=task_spec,
            result=verif_status,
            verification_summary=verif_summary,
        )

        # Enforce deterministic verification gate
        if verif_status != "passed":
            failed_steps = [s.name for s in verif_plan.steps if s.status == "failed" and s.required]
            err_msg = f"Deterministic verification failed on required steps: {', '.join(failed_steps)}"
            task_spec.transition_to("failed", err_msg)
            task_spec.save_to_file(str(run_dir / "task.yaml"))
            self._record_event(
                task_id=task_spec.task_id,
                agent_id="control_plane",
                action="task_failed",
                result=err_msg,
                spec=task_spec,
            )
            return OrchestrationResult(
                task_id=task_spec.task_id,
                task_spec=task_spec,
                final_state="failed",
                exit_code=1,
                routing_decision=routing,
                initial_delta=initial_delta,
                final_delta=current_delta,
                review_cycles=review_cycles,
                reconciliation=latest_reconciliation,
                verification_plan=verif_plan,
                howlframe_audit_status=hf_audit_status,
                howlframe_audit_match=hf_audit_match,
                remediation_cycles_count=remediation_count,
                duration_seconds=round(time.time() - start_time, 3),
                error_message=err_msg,
                run_dir=str(run_dir),
            )

        # --------------------------------------------------------------------
        # Stage 7: Human Authority Boundary Gate (awaiting_human)
        # --------------------------------------------------------------------
        actions_to_check = list(planned_actions or [])
        if any(kw in task_spec.objective.lower() for kw in ["deploy", "terraform apply", "kubectl apply", "drop table"]):
            actions_to_check.append(task_spec.objective)

        boundary_res = HumanBoundaryGate.evaluate(
            task=task_spec,
            planned_actions=actions_to_check,
            change_summary=f"Changed {len(current_delta.files_modified) + len(current_delta.files_added)} files (+{current_delta.insertions}/-{current_delta.deletions})",
            reconciliation=latest_reconciliation,
            verification=verif_plan,
        )

        if boundary_res.requires_human_approval:
            task_spec.transition_to("awaiting_human", f"Human authority boundary triggered: {boundary_res.triggered_boundaries}")
            task_spec.save_to_file(str(run_dir / "task.yaml"))

            if boundary_res.decision_packet:
                (run_dir / "decision_packet.md").write_text(boundary_res.decision_packet.render_markdown(), encoding="utf-8")

            self._record_event(
                task_id=task_spec.task_id,
                agent_id="control_plane",
                action="human_boundary_triggered",
                spec=task_spec,
                metadata={"boundaries": boundary_res.triggered_boundaries},
            )

            return OrchestrationResult(
                task_id=task_spec.task_id,
                task_spec=task_spec,
                final_state="awaiting_human",
                exit_code=2,
                routing_decision=routing,
                initial_delta=initial_delta,
                final_delta=current_delta,
                review_cycles=review_cycles,
                reconciliation=latest_reconciliation,
                verification_plan=verif_plan,
                boundary_result=boundary_res,
                howlframe_audit_status=hf_audit_status,
                howlframe_audit_match=hf_audit_match,
                remediation_cycles_count=remediation_count,
                duration_seconds=round(time.time() - start_time, 3),
                run_dir=str(run_dir),
            )

        # --------------------------------------------------------------------
        # Stage 8: Governed Completion (complete)
        # --------------------------------------------------------------------
        task_spec.transition_to("complete", "All reviews, reconciliations, deterministic verifications, and policies passed.")
        task_spec.save_to_file(str(run_dir / "task.yaml"))

        # Generate summary markdown
        summary_md = self._render_summary_markdown(
            task=task_spec,
            routing=routing,
            delta=current_delta,
            review_cycles=review_cycles,
            verif_plan=verif_plan,
            remediation_count=remediation_count,
            hf_status=hf_audit_status,
        )
        (run_dir / "summary.md").write_text(summary_md, encoding="utf-8")

        self._record_event(
            task_id=task_spec.task_id,
            agent_id="control_plane",
            action="task_completed",
            spec=task_spec,
            metadata={
                "remediation_cycles": remediation_count,
                "verification_status": verif_status,
                "files_changed": len(current_delta.files_modified) + len(current_delta.files_added),
            },
        )

        return OrchestrationResult(
            task_id=task_spec.task_id,
            task_spec=task_spec,
            final_state="complete",
            exit_code=0,
            routing_decision=routing,
            initial_delta=initial_delta,
            final_delta=current_delta,
            review_cycles=review_cycles,
            reconciliation=latest_reconciliation,
            verification_plan=verif_plan,
            boundary_result=boundary_res,
            howlframe_audit_status=hf_audit_status,
            howlframe_audit_match=hf_audit_match,
            remediation_cycles_count=remediation_count,
            duration_seconds=round(time.time() - start_time, 3),
            run_dir=str(run_dir),
        )

    def _build_remediation_prompt(
        self,
        task: TaskSpec,
        diff_content: str,
        findings: List[ReviewFinding],
    ) -> str:
        """Constructs an actionable remediation prompt with confirmed defect evidence."""
        lines = [
            f"# Remediation Request for Task `{task.task_id}`",
            f"**Objective:** {task.objective}",
            "",
            "## Identified Defects to Remediate",
        ]
        for f in findings:
            lines.append(f"### [{f.severity.upper()}] {f.title} ({f.reviewer_role})")
            if f.location:
                lines.append(f"- **Location:** `{f.location}`")
            if f.claim:
                lines.append(f"- **Claim:** {f.claim}")
            if f.evidence:
                lines.append(f"- **Evidence / Failure Case:** {f.evidence}")
            if f.suggested_fix:
                lines.append(f"- **Suggested Fix:** {f.suggested_fix}")
            lines.append("")

        lines.extend([
            "## Current Implementation Diff",
            "```diff",
            diff_content,
            "```",
            "",
            "## Instructions",
            "Fix the reported defects in the repository. Ensure all edge cases and tests pass.",
        ])
        return "\n".join(lines)

    def _render_summary_markdown(
        self,
        task: TaskSpec,
        routing: RoutingDecision,
        delta: RepositoryDelta,
        review_cycles: List[ReviewCycleResult],
        verif_plan: VerificationPlan,
        remediation_count: int,
        hf_status: Optional[str],
    ) -> str:
        lines = [
            f"# Governed Task Run Summary: `{task.task_id}`",
            "",
            "## Overview",
            f"- **Objective:** {task.objective}",
            f"- **Repository:** {self.target_repo.name}",
            f"- **Final State:** `{task.current_state.upper()}`",
            f"- **Implementing Agent:** {routing.selected_agent_name} (`{routing.selected_agent_id}`)",
            f"- **Reasoning Tier:** {routing.reasoning_tier}",
            f"- **HowlFrame Shadow Audit:** {hf_status or 'N/A'}",
            "",
            "## Repository Changes",
            f"- **Files Added:** {len(delta.files_added)}",
            f"- **Files Modified:** {len(delta.files_modified)}",
            f"- **Files Deleted:** {len(delta.files_deleted)}",
            f"- **Total Insertions:** +{delta.insertions}",
            f"- **Total Deletions:** -{delta.deletions}",
            "",
            "## Review & Remediation",
            f"- **Total Review Cycles:** {len(review_cycles)}",
            f"- **Remediation Cycles:** {remediation_count}",
        ]
        if review_cycles:
            last_cycle = review_cycles[-1]
            lines.append(f"- **Final Review Status:** `{last_cycle.status}`")
            for role, res in sorted(last_cycle.reviewer_results.items()):
                lines.append(f"  - `{role}`: {res.status} ({len(res.findings)} findings)")

        lines.extend([
            "",
            "## Deterministic Verification",
            f"- **Overall Status:** `{verif_plan.overall_status.upper()}`",
        ])
        for step in verif_plan.steps:
            mark = "✓" if step.status == "verified" else "✗"
            lines.append(f"- [{mark}] **{step.name}** (`{step.category}`): {step.status} (exit {step.exit_code})")

        lines.extend([
            "",
            "---",
            "*Verified and sealed by HowlPlane AI Engineering Control Plane.*",
        ])
        return "\n".join(lines)
