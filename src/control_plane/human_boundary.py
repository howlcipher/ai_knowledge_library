#!/usr/bin/env python3
"""
human_boundary.py

Human authority boundary enforcement and structured decision packet generation.
Guarantees that high-risk, destructive, financial, or security-sensitive actions
pause at AWAITING_HUMAN with complete evidence before proceeding.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Optional, Tuple, Union

from src.control_plane.evidence_ledger import EvidenceEntry, EvidenceLedger
from src.control_plane.hygiene_policy import (
    PolicyChangeType,
    PolicyEvaluationResult,
)
from src.control_plane.reconciliation import ReconciliationResult
from src.control_plane.task_spec import TaskSpec
from src.control_plane.verification import VerificationPlan


class HumanLifecycleError(Exception):
    """Base exception for human decision and lifecycle errors."""
    pass


class TaskRunNotFoundError(HumanLifecycleError):
    """Raised when the specified task run directory is not found."""
    pass


class InvalidTaskStateError(HumanLifecycleError):
    """Raised when an operation is invalid for the current task state."""
    pass


class ContradictoryDecisionError(HumanLifecycleError):
    """Raised when a decision contradicts a previous immutable decision."""
    pass


class RepositoryDriftError(HumanLifecycleError):
    """Raised when repository state drifts between review and approval/resume."""
    pass


class StaleApprovalError(HumanLifecycleError):
    """Raised when repository drift invalidates an existing approval."""
    pass


class ApprovalRequiredError(HumanLifecycleError):
    """Raised when resuming a task that has not been approved."""
    pass

HUMAN_BOUNDARY_TRIGGERS = {
    "production_deployment": "Production deployment or live environment modification",
    "infrastructure_apply": "Infrastructure-as-code apply (e.g. terraform apply, k8s apply)",
    "destructive_database_change": "Destructive database migration (DROP TABLE/COLUMN, truncate)",
    "credential_provisioning": "Credential, token, or secret creation/rotation",
    "paid_service_usage": "Paid API or service consumption requiring user billing approval",
    "external_dependency_addition": "Adding new external dependencies or modifying license scope",
    "external_messaging": "Sending outbound emails, messages, webhooks, or notifications",
    "package_publishing": "Publishing packages or binaries to public registries or releases",
    "job_submission": "Submitting job applications, resumes, or external forms",
    "security_policy_exception": "Overriding or relaxing established security or anti-manipulation rules",
    "slop_debt_acceptance": (
        "Accepting new repository debt tombstone or repointing existing debt without prior policy authorization"
    ),
    "hygiene_policy_weakening": (
        "Weakening repository hygiene scan scope, ignore patterns, detector parameters, or provider settings"
    ),
    "hygiene_policy_violation": (
        "Prohibited repository hygiene policy violation (ceiling increase or configuration deletion)"
    ),
}


@dataclass
class HumanDecisionPacket:
    """Concise decision packet presented to a human operator for sign-off."""

    task_id: str
    objective: str
    change_summary: str
    boundary_triggers: List[str]
    evidence: List[str]
    risks: List[str]
    review_findings_summary: Dict[str, int]
    verification_status: str
    recommended_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def render_markdown(self) -> str:
        triggers_str = "\n".join(f"- ⚠️ **{t}**: {HUMAN_BOUNDARY_TRIGGERS.get(t, t)}" for t in self.boundary_triggers)
        evidence_str = "\n".join(f"- {e}" for e in self.evidence) or "None recorded."
        risks_str = "\n".join(f"- {r}" for r in self.risks) or "None recorded."
        findings_text = (
            f"{self.review_findings_summary.get('total', 0)} total ("
            f"{self.review_findings_summary.get('blocker', 0)} blockers, "
            f"{self.review_findings_summary.get('high', 0)} highs)"
        )

        return f"""# 🛑 Human Authority Decision Packet: Task `{self.task_id}`

## Objective
{self.objective}

## Boundary Triggers (Human Authorization Required)
{triggers_str}

## Proposed Change Summary
{self.change_summary}

## Verification Status
- **Automated Verification:** `{self.verification_status}`
- **Review Findings:** {findings_text}

## Key Evidence
{evidence_str}

## Identified Risks
{risks_str}

## Recommended Action
{self.recommended_action}

---
*Awaiting explicit human approval. Lack of response is treated as DENIED (fail-closed).*
"""


@dataclass
class BoundaryCheckResult:
    """Result of evaluating human authority boundaries."""

    requires_human_approval: bool
    triggered_boundaries: List[str] = field(default_factory=list)
    decision_packet: Optional[HumanDecisionPacket] = None


class HumanBoundaryGate:
    """Evaluates task intent, actions, and risk against human authority policies."""

    @classmethod
    def evaluate(
        cls,
        task: TaskSpec,
        planned_actions: List[str],
        change_summary: str = "",
        reconciliation: Optional[ReconciliationResult] = None,
        verification: Optional[VerificationPlan] = None,
        hygiene_policy: Optional[PolicyEvaluationResult] = None,
    ) -> BoundaryCheckResult:
        """
        Determines whether the task hits a human authority boundary.
        Distinguishes quality improvements (autonomously permitted) from debt acceptance / weakening.
        """
        triggers: List[str] = []

        # 1. Inspect task requirements
        if task.human_approval_requirements:
            for req in task.human_approval_requirements:
                if req in HUMAN_BOUNDARY_TRIGGERS and req not in triggers:
                    triggers.append(req)

        # 2. Inspect planned actions and commands
        actions_str = " ".join(planned_actions).lower()
        if "terraform apply" in actions_str or "kubectl apply" in actions_str:
            if "infrastructure_apply" not in triggers:
                triggers.append("infrastructure_apply")

        if "drop table" in actions_str or "drop column" in actions_str or "truncate" in actions_str:
            if "destructive_database_change" not in triggers:
                triggers.append("destructive_database_change")

        if "publish" in actions_str or "twine upload" in actions_str or "npm publish" in actions_str:
            if "package_publishing" not in triggers:
                triggers.append("package_publishing")

        if "sendmail" in actions_str or "smtp" in actions_str or "webhook" in actions_str:
            if "external_messaging" not in triggers:
                triggers.append("external_messaging")

        # 3. Evaluate semantic hygiene policy results
        if hygiene_policy:
            if hygiene_policy.is_hard_rejected:
                if "hygiene_policy_violation" not in triggers:
                    triggers.append("hygiene_policy_violation")
            if hygiene_policy.verdict == PolicyChangeType.DEBT_ACCEPTANCE:
                if "slop_debt_acceptance" not in triggers:
                    triggers.append("slop_debt_acceptance")
            elif hygiene_policy.verdict == PolicyChangeType.WEAKENING:
                if "hygiene_policy_weakening" not in triggers:
                    triggers.append("hygiene_policy_weakening")
            elif hygiene_policy.verdict == PolicyChangeType.UNKNOWN:
                if "security_policy_exception" not in triggers:
                    triggers.append("security_policy_exception")
        else:
            # Fallback heuristic when policy evaluation object is not pre-computed
            if (
                "tombstone add" in actions_str
                or "accept_debt" in actions_str
                or "write .slop/tombstones" in actions_str
                or ("tombstone" in actions_str and "delete" not in actions_str and "stale" not in actions_str)
            ):
                if "slop_debt_acceptance" not in triggers:
                    triggers.append("slop_debt_acceptance")

            if "ceiling increase" in actions_str:
                if "hygiene_policy_violation" not in triggers:
                    triggers.append("hygiene_policy_violation")

        # 4. Inspect reconciliation findings for unresolved blockers or security human reviews
        if reconciliation and reconciliation.requires_human_judgment:
            if "security_policy_exception" not in triggers:
                triggers.append("security_policy_exception")

        # 5. Critical risk tasks always trigger human authority
        if task.risk_level == "critical" and "production_deployment" not in triggers:
            triggers.append("production_deployment")

        if not triggers:
            return BoundaryCheckResult(requires_human_approval=False)

        # Build decision packet
        evidence_list: List[str] = []
        if verification:
            for step in verification.steps:
                evidence_list.append(f"Step '{step.name}': {step.status} (exit {step.exit_code})")

        if hygiene_policy and hygiene_policy.changes:
            for c in hygiene_policy.changes:
                evidence_list.append(f"Policy Change [{c.change_type.value.upper()}]: {c.description}")

        risks_list: List[str] = []
        for t in triggers:
            risks_list.append(f"Policy boundary '{t}': {HUMAN_BOUNDARY_TRIGGERS.get(t, t)}")

        findings_summary = {
            "total": len(reconciliation.findings) if reconciliation else 0,
            "blocker": reconciliation.unresolved_blockers if reconciliation else 0,
            "high": reconciliation.unresolved_highs if reconciliation else 0,
        }

        rec_action = "Review diff and evidence packet, then provide explicit approval or rejection."
        if "hygiene_policy_violation" in triggers:
            rec_action = "HARD REJECT: Prohibited ceiling inflation or policy violation must be remediated in code."

        summary_text = change_summary
        if not summary_text and hygiene_policy:
            summary_text = hygiene_policy.summary
        if not summary_text:
            summary_text = "Pending review & human confirmation."

        packet = HumanDecisionPacket(
            task_id=task.task_id,
            objective=task.objective,
            change_summary=summary_text,
            boundary_triggers=triggers,
            evidence=evidence_list,
            risks=risks_list,
            review_findings_summary=findings_summary,
            verification_status=verification.overall_status if verification else "unverified",
            recommended_action=rec_action,
        )

        return BoundaryCheckResult(
            requires_human_approval=True,
            triggered_boundaries=triggers,
            decision_packet=packet,
        )


HUMAN_DECISION_SCHEMA_VERSION = "howlplane.human_decision/v1"


@dataclass
class RepositoryStateFingerprint:
    """Fingerprint of the repository state bound to an authorization decision."""

    commit_sha: str
    dirty: bool
    diff_sha256: str
    files_modified: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryStateFingerprint":
        return cls(
            commit_sha=data.get("commit_sha", ""),
            dirty=data.get("dirty", False),
            diff_sha256=data.get("diff_sha256", ""),
            files_modified=data.get("files_modified", []),
        )


@dataclass
class HumanDecisionRecord:
    """Durable, structured human decision artifact scoped to a task and reviewed repository state."""

    task_id: str
    decision: str  # "approved" | "rejected"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    boundary_triggers: List[str] = field(default_factory=list)
    operator_source: str = "cli"
    reason: Optional[str] = None
    repository: str = ""
    repository_state: Optional[RepositoryStateFingerprint] = None
    decision_packet_sha256: Optional[str] = None
    schema: str = HUMAN_DECISION_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.repository_state:
            d["repository_state"] = self.repository_state.to_dict()
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HumanDecisionRecord":
        repo_state_data = data.get("repository_state")
        repo_state = (
            RepositoryStateFingerprint.from_dict(repo_state_data)
            if repo_state_data
            else None
        )
        return cls(
            task_id=data["task_id"],
            decision=data["decision"],
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            boundary_triggers=data.get("boundary_triggers", []),
            operator_source=data.get("operator_source", "cli"),
            reason=data.get("reason"),
            repository=data.get("repository", ""),
            repository_state=repo_state,
            decision_packet_sha256=data.get("decision_packet_sha256"),
            schema=data.get("schema", HUMAN_DECISION_SCHEMA_VERSION),
        )

    def save_to_file(self, path: Union[str, Path]) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load_from_file(cls, path: Union[str, Path]) -> "HumanDecisionRecord":
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Decision file not found: {path}")
        return cls.from_dict(json.loads(p.read_text(encoding="utf-8")))


def compute_repository_fingerprint(
    repo_dir: Union[str, Path],
    task_run_dir: Optional[Union[str, Path]] = None,
) -> RepositoryStateFingerprint:
    """
    Computes a cryptographic fingerprint of the repository state bound to this task.
    Uses git HEAD commit SHA, status porcelain, and attributable diff content.
    """
    root = Path(repo_dir).resolve()
    res_sha = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    commit_sha = res_sha.stdout.strip() if res_sha.returncode == 0 else "HEAD_UNKNOWN"

    res_status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    status_out = res_status.stdout if res_status.returncode == 0 else ""
    dirty = bool(status_out.strip())

    files: List[str] = []
    for line in status_out.splitlines():
        if line.strip():
            path_part = line[3:].strip()
            if " -> " in path_part:
                path_part = path_part.split(" -> ")[1].strip()
            if (
                path_part.startswith(".task_runs")
                or path_part.startswith("logs/control_plane")
                or path_part.endswith(".jsonl")
            ):
                continue
            files.append(path_part)

    diff_text = ""
    if task_run_dir and (Path(task_run_dir) / "baseline.json").is_file():
        try:
            from src.control_plane.git_baseline import capture_delta, GitBaseline
            baseline_data = json.loads((Path(task_run_dir) / "baseline.json").read_text(encoding="utf-8"))
            baseline = GitBaseline.from_dict(baseline_data)
            delta = capture_delta(root, baseline)
            diff_text = delta.diff_content
        except Exception:
            pass

    if not diff_text:
        res_diff = subprocess.run(
            ["git", "-C", str(root), "diff", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        diff_text = res_diff.stdout if res_diff.returncode == 0 else ""
        for f_name in sorted(files):
            f_path = root / f_name
            if f_path.is_file():
                try:
                    diff_text += f"\n--- {f_name} ---\n" + f_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    pass

    diff_sha256 = hashlib.sha256(diff_text.encode("utf-8")).hexdigest()
    return RepositoryStateFingerprint(
        commit_sha=commit_sha,
        dirty=dirty,
        diff_sha256=diff_sha256,
        files_modified=sorted(files),
    )


def check_repository_drift(
    approved_fingerprint: RepositoryStateFingerprint,
    current_fingerprint: RepositoryStateFingerprint,
) -> Tuple[bool, Optional[str]]:
    """
    Compares the approved repository state fingerprint with current repository state.
    Returns (has_drift, drift_reason).
    """
    if approved_fingerprint.commit_sha != current_fingerprint.commit_sha:
        return True, f"HEAD commit changed (approved {approved_fingerprint.commit_sha[:8]}, current {current_fingerprint.commit_sha[:8]})"

    if approved_fingerprint.diff_sha256 != current_fingerprint.diff_sha256:
        return True, "Attributable diff content modified since authorization"

    if approved_fingerprint.files_modified != current_fingerprint.files_modified:
        return True, f"Modified files changed (approved {approved_fingerprint.files_modified}, current {current_fingerprint.files_modified})"

    return False, None


class HumanLifecycleManager:
    """
    Orchestrates human decision capture, state validation, drift verification,
    idempotency enforcement, and task resumption.
    """

    @staticmethod
    def get_run_dir(target_repo: Union[str, Path], task_id: str) -> Path:
        return Path(target_repo).resolve() / ".task_runs" / task_id

    @staticmethod
    def load_task_spec(run_dir: Path) -> TaskSpec:
        task_file = run_dir / "task.yaml"
        if not task_file.is_file():
            raise TaskRunNotFoundError(f"Task spec not found at {task_file}")
        return TaskSpec.load_from_file(str(task_file))

    @staticmethod
    def load_decision(run_dir: Path) -> Optional[HumanDecisionRecord]:
        dec_file = run_dir / "human_decision.json"
        if not dec_file.is_file():
            return None
        return HumanDecisionRecord.load_from_file(str(dec_file))

    @classmethod
    def _prepare_decision(
        cls,
        target_repo: Union[str, Path],
        task_id: str,
        decision: str,
    ) -> Tuple[Path, TaskSpec, RepositoryStateFingerprint, Optional[str], List[str]]:
        run_dir = cls.get_run_dir(target_repo, task_id)
        if not run_dir.is_dir() or not (run_dir / "task.yaml").is_file():
            raise TaskRunNotFoundError(f"Task run '{task_id}' not found in {target_repo}/.task_runs")

        task_spec = cls.load_task_spec(run_dir)

        existing = cls.load_decision(run_dir)
        if existing:
            if existing.decision == decision:
                return run_dir, task_spec, None, None, None
            opp = "APPROVED" if decision == "rejected" else "REJECTED"
            raise ContradictoryDecisionError(
                f"Task '{task_id}' was previously {opp}. Contradictory {decision} rejected (fail-closed)."
            )

        if decision == "approved" and task_spec.current_state != "awaiting_human":
            if task_spec.current_state == "complete":
                raise InvalidTaskStateError(f"Task '{task_id}' is already COMPLETE.")
            if task_spec.current_state == "failed":
                raise InvalidTaskStateError(f"Task '{task_id}' is in FAILED state. Cannot approve a failed task.")
            raise InvalidTaskStateError(
                f"Task '{task_id}' is in state '{task_spec.current_state}'. Only tasks in AWAITING_HUMAN state can be approved."
            )

        current_fp = compute_repository_fingerprint(target_repo, run_dir)
        dp_file = run_dir / "decision_packet.md"
        dp_sha = (
            hashlib.sha256(dp_file.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            if dp_file.is_file()
            else None
        )

        triggers = list(task_spec.human_approval_requirements or [])
        if not triggers and dp_file.is_file():
            for line in dp_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("- ⚠️ **") and "**:" in line:
                    t_name = line.split("**")[1].strip()
                    if t_name and t_name not in triggers:
                        triggers.append(t_name)

        return run_dir, task_spec, current_fp, dp_sha, triggers

    @classmethod
    def approve(
        cls,
        target_repo: Union[str, Path],
        task_id: str,
        reason: Optional[str] = None,
        operator_source: str = "cli",
        ledger: Optional[EvidenceLedger] = None,
    ) -> HumanDecisionRecord:
        """
        Records an explicit human approval for a task awaiting authorization.
        Enforces idempotency, fail-closed contradictory checks, and repository state binding.
        """
        run_dir, task_spec, current_fp, dp_sha, triggers = cls._prepare_decision(
            target_repo, task_id, "approved"
        )
        if current_fp is None:
            return cls.load_decision(run_dir)

        patch_file = run_dir / "diff.patch"
        if patch_file.is_file():
            reviewed_diff = patch_file.read_text(encoding="utf-8")
            reviewed_sha = hashlib.sha256(reviewed_diff.encode("utf-8")).hexdigest()
            if current_fp.diff_sha256 != reviewed_sha:
                raise RepositoryDriftError(
                    f"Repository code has changed since task '{task_id}' was reviewed. Approval cannot authorize unreviewed changes."
                )

        record = HumanDecisionRecord(
            task_id=task_id,
            decision="approved",
            timestamp=datetime.now(timezone.utc).isoformat(),
            boundary_triggers=triggers,
            operator_source=operator_source,
            reason=reason,
            repository=Path(target_repo).name,
            repository_state=current_fp,
            decision_packet_sha256=dp_sha,
        )
        record.save_to_file(run_dir / "human_decision.json")

        if ledger:
            ledger.append_entry(
                EvidenceEntry(
                    task_id=task_id,
                    agent_id="human_operator",
                    action="human_approval",
                    result="approved",
                    human_decision="approved",
                    artifact=str(run_dir / "human_decision.json"),
                    metadata={
                        "reason": reason,
                        "operator_source": operator_source,
                        "boundaries": triggers,
                        "commit_sha": current_fp.commit_sha,
                    },
                )
            )

        return record

    @classmethod
    def reject(
        cls,
        target_repo: Union[str, Path],
        task_id: str,
        reason: Optional[str] = None,
        operator_source: str = "cli",
        ledger: Optional[EvidenceLedger] = None,
    ) -> HumanDecisionRecord:
        """
        Records an explicit human rejection for a task.
        Enforces fail-closed behavior, transitions task to FAILED, and records evidence.
        """
        run_dir, task_spec, current_fp, dp_sha, triggers = cls._prepare_decision(
            target_repo, task_id, "rejected"
        )
        if current_fp is None:
            return cls.load_decision(run_dir)

        record = HumanDecisionRecord(
            task_id=task_id,
            decision="rejected",
            timestamp=datetime.now(timezone.utc).isoformat(),
            boundary_triggers=triggers,
            operator_source=operator_source,
            reason=reason,
            repository=Path(target_repo).name,
            repository_state=current_fp,
            decision_packet_sha256=dp_sha,
        )
        record.save_to_file(run_dir / "human_decision.json")

        task_spec.transition_to(
            "failed",
            f"Human operator rejected authorization: {reason or 'No reason provided'}",
        )
        task_spec.save_to_file(str(run_dir / "task.yaml"))

        if ledger:
            ledger.append_entry(
                EvidenceEntry(
                    task_id=task_id,
                    agent_id="human_operator",
                    action="human_rejection",
                    result="rejected",
                    human_decision="rejected",
                    artifact=str(run_dir / "human_decision.json"),
                    metadata={"reason": reason, "operator_source": operator_source},
                )
            )

        return record

    @classmethod
    def resume(
        cls,
        target_repo: Union[str, Path],
        task_id: str,
        orchestrator: Optional[Any] = None,
        ledger: Optional[EvidenceLedger] = None,
        control_plane_root: Optional[Union[str, Path]] = None,
    ) -> Any:
        """
        Resumes task execution from durable task-run artifacts.
        Validates approval status, repository drift, and transitions to COMPLETE.
        """
        from src.control_plane.orchestrator import OrchestrationResult

        run_dir = cls.get_run_dir(target_repo, task_id)
        if not run_dir.is_dir() or not (run_dir / "task.yaml").is_file():
            raise TaskRunNotFoundError(f"Task run '{task_id}' not found in {target_repo}/.task_runs")

        task_spec = cls.load_task_spec(run_dir)

        if task_spec.current_state == "complete":
            return OrchestrationResult(
                task_id=task_id,
                task_spec=task_spec,
                final_state="complete",
                exit_code=0,
                run_dir=str(run_dir),
            )

        if task_spec.current_state == "failed":
            dec = cls.load_decision(run_dir)
            if dec and dec.decision == "rejected":
                raise InvalidTaskStateError(
                    f"Task '{task_id}' was rejected by human operator and cannot be resumed."
                )
            raise InvalidTaskStateError(
                f"Task '{task_id}' is in FAILED state. Cannot resume a failed task without re-running."
            )

        if task_spec.current_state == "awaiting_human":
            decision = cls.load_decision(run_dir)
            if not decision:
                raise ApprovalRequiredError(
                    f"Task '{task_id}' is AWAITING_HUMAN and requires explicit human approval before resuming. Run 'ai approve {task_id}'."
                )
            if decision.decision == "rejected":
                raise InvalidTaskStateError(f"Task '{task_id}' authorization was REJECTED by human operator.")

            if decision.decision == "approved":
                # Validate repository state binding (drift check)
                current_fp = compute_repository_fingerprint(target_repo, run_dir)
                if decision.repository_state:
                    has_drift, drift_reason = check_repository_drift(decision.repository_state, current_fp)
                    if has_drift:
                        if ledger:
                            ledger.append_entry(
                                EvidenceEntry(
                                    task_id=task_id,
                                    agent_id="control_plane",
                                    action="stale_approval_detected",
                                    result=f"Repository drift detected: {drift_reason}",
                                    metadata={"drift_reason": drift_reason},
                                )
                            )
                        raise StaleApprovalError(
                            f"Repository state has drifted since approval was granted ({drift_reason}). "
                            f"Approval is STALE. Re-review and re-approval required."
                        )

                # Valid approval + no drift: resume and complete
                if ledger:
                    ledger.append_entry(
                        EvidenceEntry(
                            task_id=task_id,
                            agent_id="control_plane",
                            action="task_resumed",
                            metadata={"task_id": task_id, "resumed_from": "awaiting_human"},
                        )
                    )

                task_spec.transition_to(
                    "complete",
                    f"Human authority approved ({decision.reason or 'No reason specified'}): all gates satisfied.",
                )
                task_spec.save_to_file(str(run_dir / "task.yaml"))

                if ledger:
                    ledger.append_entry(
                        EvidenceEntry(
                            task_id=task_id,
                            agent_id="control_plane",
                            action="task_completed",
                            task_class=task_spec.task_class,
                            risk_level=task_spec.risk_level,
                            reasoning_tier=task_spec.recommended_reasoning_tier,
                            metadata={"human_approved": True, "resumed": True},
                        )
                    )

                summary_file = run_dir / "summary.md"
                if not summary_file.is_file():
                    summary_file.write_text(
                        f"# Governed Task Run Summary: `{task_id}`\n\n"
                        f"- **Objective:** {task_spec.objective}\n"
                        f"- **Final State:** `COMPLETE` (Human Approved)\n"
                        f"- **Approved At:** {decision.timestamp}\n",
                        encoding="utf-8",
                    )

                return OrchestrationResult(
                    task_id=task_id,
                    task_spec=task_spec,
                    final_state="complete",
                    exit_code=0,
                    run_dir=str(run_dir),
                )

        # For tasks interrupted in intermediate states (discovered, planned, implementing, reviewing, verifying)
        if orchestrator:
            return orchestrator.run(task_spec)
        else:
            from src.control_plane.orchestrator import GovernedTaskOrchestrator
            orch = GovernedTaskOrchestrator(
                target_repo=target_repo,
                control_plane_root=control_plane_root,
            )
            return orch.run(task_spec)
