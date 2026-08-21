#!/usr/bin/env python3
"""
review_runner.py

Executes independent adversarial reviewers against actual implementation diffs,
validates structured output schemas, and determines targeted re-review strategies.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json, re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import yaml

from src.control_plane.agent_execution import AgentBackend, AgentBackendRegistry, AgentExecutionResult
from src.control_plane.reconciliation import ReviewFinding, ReconciliationResult, ReviewReconciler, VALID_SEVERITIES
from src.control_plane.reviewers import get_reviewer_role, ReviewerRole, build_skill_context
from src.control_plane.task_spec import TaskSpec

REVIEW_RUN_SCHEMA_VERSION = "howlplane.review_runner/v1"


@dataclass
class SingleReviewResult:
    """Result of an individual independent reviewer execution."""

    reviewer_role: str
    reviewer_name: str
    status: str  # "clean", "findings_detected", "reviewer_failure", "malformed_output"
    findings: List[ReviewFinding] = field(default_factory=list)
    raw_output: str = ""
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    agent_result: Optional[AgentExecutionResult] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reviewer_role": self.reviewer_role,
            "reviewer_name": self.reviewer_name,
            "status": self.status,
            "findings": [f.to_dict() for f in self.findings],
            "raw_output": self.raw_output,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
            "agent_result": self.agent_result.to_dict() if self.agent_result else None,
            "timestamp": self.timestamp,
        }


@dataclass
class ReviewCycleResult:
    """Consolidated result of a complete review cycle across multiple reviewers."""

    cycle_index: int
    reviewer_results: Dict[str, SingleReviewResult] = field(default_factory=dict)
    all_findings: List[ReviewFinding] = field(default_factory=list)
    reconciliation: Optional[ReconciliationResult] = None
    status: str = "clean"  # "clean", "has_findings", "review_failure"
    requires_remediation: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    schema: str = REVIEW_RUN_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_index": self.cycle_index,
            "status": self.status,
            "requires_remediation": self.requires_remediation,
            "reviewer_results": {k: v.to_dict() for k, v in self.reviewer_results.items()},
            "all_findings": [f.to_dict() for f in self.all_findings],
            "reconciliation": self.reconciliation.to_dict() if self.reconciliation else None,
            "timestamp": self.timestamp,
            "schema": self.schema,
        }


def parse_and_validate_findings(
    raw_output: str,
    reviewer_role: str,
) -> Tuple[List[ReviewFinding], Optional[str]]:
    """
    Parses YAML/JSON findings from raw reviewer output.
    Returns (findings, error_message).
    If output is malformed, returns a synthetic finding signaling REVIEWER_FAILURE.
    """
    if not raw_output or not raw_output.strip():
        # Clean / empty review output
        return [], None

    clean_text = raw_output.strip()

    # Extract yaml / json code block if wrapped in markdown
    code_block_match = re.search(r"```(?:yaml|json)?\s*\n([\s\S]*?)\n```", clean_text)
    if code_block_match:
        payload_text = code_block_match.group(1).strip()
    else:
        payload_text = clean_text

    try:
        parsed = yaml.safe_load(payload_text)
    except Exception as exc:
        err_msg = f"Malformed reviewer output YAML: {exc}"
        failure_finding = ReviewFinding(
            id=f"ERR-{reviewer_role[:4].upper()}-001",
            reviewer_role=reviewer_role,
            title=f"Malformed reviewer output from {reviewer_role}",
            severity="high",
            category="other",
            description=f"Reviewer output failed schema validation: {err_msg}",
            status="open",
            claim="Reviewer produced unparseable output format",
            evidence=raw_output[:500],
        )
        return [failure_finding], err_msg

    if parsed is None:
        return [], None

    # Normalization of parsed content
    findings_list: List[Dict[str, Any]] = []
    if isinstance(parsed, dict):
        if "findings" in parsed:
            raw_f = parsed.get("findings")
            if isinstance(raw_f, list):
                findings_list = raw_f
            elif raw_f is None:
                findings_list = []
            else:
                err_msg = f"'findings' field in output must be a list, got {type(raw_f)}"
                return [_make_err_finding(reviewer_role, err_msg, raw_output)], err_msg
        else:
            # Maybe single finding object
            if "title" in parsed or "severity" in parsed:
                findings_list = [parsed]
            elif not parsed:
                return [], None
            else:
                err_msg = "Reviewer dictionary output missing 'findings' list"
                return [_make_err_finding(reviewer_role, err_msg, raw_output)], err_msg
    elif isinstance(parsed, list):
        findings_list = parsed
    elif isinstance(parsed, str) and any(w in parsed.lower() for w in ["no defects", "zero findings", "looks good", "clean", "passed", "no issues"]):
        return [], None
    else:
        err_msg = f"Unexpected reviewer output type: {type(parsed)}"
        return [_make_err_finding(reviewer_role, err_msg, raw_output)], err_msg

    validated_findings: List[ReviewFinding] = []
    for idx, item in enumerate(findings_list, 1):
        if not isinstance(item, dict):
            err_msg = f"Finding at index {idx} is not a valid dictionary"
            return [_make_err_finding(reviewer_role, err_msg, raw_output)], err_msg

        f_id = str(item.get("id") or f"F{idx:03d}")
        title = str(item.get("title") or f"Issue found by {reviewer_role}")
        severity = str(item.get("severity") or "medium").lower().strip()
        if severity not in VALID_SEVERITIES:
            severity = "medium"

        category = str(item.get("category") or "correctness").lower().strip()
        description = str(item.get("description") or item.get("claim") or title)
        location = item.get("location")
        claim = item.get("claim")
        evidence = item.get("evidence")
        suggested_fix = item.get("suggested_fix")
        component = item.get("component")

        finding = ReviewFinding(
            id=f_id,
            reviewer_role=reviewer_role,
            title=title,
            severity=severity,
            category=category,
            description=description,
            component=component,
            claim=claim,
            location=location,
            evidence=evidence,
            suggested_fix=suggested_fix,
            status="open",
        )
        validated_findings.append(finding)

    return validated_findings, None


def _make_err_finding(reviewer_role: str, err_msg: str, raw_output: str) -> ReviewFinding:
    return ReviewFinding(
        id=f"ERR-{reviewer_role[:4].upper()}-001",
        reviewer_role=reviewer_role,
        title=f"Malformed reviewer output from {reviewer_role}",
        severity="high",
        category="other",
        description=f"Reviewer output failed validation: {err_msg}",
        status="open",
        claim="Reviewer produced unparseable output format",
        evidence=raw_output[:500],
    )


class ReviewRunner:
    """Orchestrates independent review runs, output parsing, and reconciliation."""

    @classmethod
    def execute_review_cycle(
        cls,
        task: TaskSpec,
        diff_content: str,
        reviewer_roles: List[str],
        cwd: Union[str, Path],
        backend: Optional[AgentBackend] = None,
        cycle_index: int = 1,
        reviewer_agent_mapping: Optional[Dict[str, str]] = None,
        custom_reviewer_fn: Optional[Callable[[str, str, TaskSpec], str]] = None,
        run_dir: Optional[Union[str, Path]] = None,
    ) -> ReviewCycleResult:
        """
        Executes each specified reviewer independently against the actual implementation diff.
        Preserves already-completed reviewer artifacts from previous interrupted runs.
        """
        target_cwd = Path(cwd).resolve()
        reviewer_results: Dict[str, SingleReviewResult] = {}
        all_findings: List[ReviewFinding] = []
        has_failure = False

        skill_context = build_skill_context(task)

        # Establish cycle directory for incremental checkpointing
        cycle_dir: Optional[Path] = None
        if run_dir:
            r_path = Path(run_dir).resolve()
            if cycle_index == 1:
                cycle_dir = r_path / "reviews"
            else:
                cycle_dir = r_path / "remediation" / f"cycle-{cycle_index - 1:02d}" / "re_review"
            cycle_dir.mkdir(parents=True, exist_ok=True)

        for role_id in reviewer_roles:
            role = get_reviewer_role(role_id)
            role_name = role.name if role else role_id

            # Check if this reviewer already completed in a previous interrupted run
            cached_result: Optional[SingleReviewResult] = None
            if cycle_dir:
                cached_md = cycle_dir / f"{role_id}.md"
                cached_yaml = cycle_dir / f"{role_id}_findings.yaml"
                if cached_md.is_file() and cached_yaml.is_file():
                    try:
                        c_raw = cached_md.read_text(encoding="utf-8")
                        raw_data = yaml.safe_load(cached_yaml.read_text(encoding="utf-8")) or []
                        if isinstance(raw_data, dict):
                            c_findings_data = raw_data.get("findings", [])
                        elif isinstance(raw_data, list):
                            c_findings_data = raw_data
                        else:
                            c_findings_data = []
                        c_findings = [
                            ReviewFinding.from_dict(f) if isinstance(f, dict) else f
                            for f in c_findings_data
                        ]
                        cached_result = SingleReviewResult(
                            reviewer_role=role_id,
                            reviewer_name=role_name,
                            status="findings_detected" if c_findings else "clean",
                            findings=c_findings,
                            raw_output=c_raw,
                            error_message=None,
                            duration_seconds=0.0,
                        )
                    except Exception:
                        cached_result = None

            if cached_result is not None:
                reviewer_results[role_id] = cached_result
                all_findings.extend(cached_result.findings)
                continue

            # Render brief with the REAL implementation diff and skill context
            brief = (
                role.render_brief(task=task, diff_content=diff_content, context=skill_context)
                if role
                else f"# Review Brief for {role_id}\n{skill_context or ''}\n```diff\n{diff_content}\n```"
            )

            raw_output = ""
            err_message = None
            agent_res: Optional[AgentExecutionResult] = None
            duration = 0.0

            if custom_reviewer_fn:
                try:
                    raw_output = custom_reviewer_fn(role_id, diff_content, task)
                except Exception as exc:
                    err_message = str(exc)
                    has_failure = True
            else:
                agent_id = (reviewer_agent_mapping or {}).get(role_id) or "claude_code"
                selected_backend = backend or AgentBackendRegistry.get_backend(agent_id)
                agent_res = selected_backend.execute(
                    task=task,
                    cwd=target_cwd,
                    role=role_id,
                    prompt_override=brief,
                )
                duration = agent_res.duration_seconds
                if agent_res.success:
                    raw_output = agent_res.stdout
                else:
                    err_message = agent_res.stderr or agent_res.error_message
                    has_failure = True

            findings, parse_err = parse_and_validate_findings(raw_output, role_id)
            if parse_err:
                has_failure = True
                status = "malformed_output"
            elif err_message:
                status = "reviewer_failure"
            elif findings:
                status = "findings_detected"
            else:
                status = "clean"

            single_res = SingleReviewResult(
                reviewer_role=role_id,
                reviewer_name=role_name,
                status=status,
                findings=findings,
                raw_output=raw_output,
                error_message=err_message or parse_err,
                duration_seconds=duration,
                agent_result=agent_res,
            )
            reviewer_results[role_id] = single_res
            all_findings.extend(findings)

            # Persist individual reviewer artifact incrementally
            if cycle_dir:
                try:
                    from src.control_plane.atomic_io import atomic_write_text, atomic_write_yaml
                    atomic_write_text(cycle_dir / f"{role_id}.md", raw_output)
                    atomic_write_yaml(
                        cycle_dir / f"{role_id}_findings.yaml",
                        [f.to_dict() for f in findings],
                        sort_keys=False,
                    )
                except Exception:
                    pass

        # Run reconciliation across all gathered findings
        reconciliation = ReviewReconciler.reconcile(all_findings) if all_findings else None

        # Check if remediation is needed: unresolved blockers > 0 or unresolved highs > 0
        requires_remediation = False
        if reconciliation:
            if reconciliation.unresolved_blockers > 0 or reconciliation.unresolved_highs > 0:
                requires_remediation = True
            elif reconciliation.confirmed or reconciliation.likely:
                requires_remediation = True

        overall_status = "review_failure" if has_failure else ("has_findings" if all_findings else "clean")

        return ReviewCycleResult(
            cycle_index=cycle_index,
            reviewer_results=reviewer_results,
            all_findings=all_findings,
            reconciliation=reconciliation,
            status=overall_status,
            requires_remediation=requires_remediation,
        )

    @classmethod
    def determine_re_review_roles(
        cls,
        findings: List[ReviewFinding],
        original_roles: List[str],
    ) -> List[str]:
        """
        Deterministically selects targeted reviewers for re-review after remediation.
        """
        if not findings:
            return list(original_roles)

        selected: Set[str] = set()
        for f in findings:
            cat = (f.category or "").lower()
            role = f.reviewer_role

            if role:
                selected.add(role)

            if cat in ("security", "vuln", "auth"):
                selected.update(["security-reviewer", "correctness-reviewer", "test-falsifier"])
            elif cat in ("architecture", "coupling", "boundary"):
                selected.update(["architecture-reviewer", "regression-reviewer", "correctness-reviewer"])
            elif cat in ("regression", "breaking_change"):
                selected.update(["regression-reviewer", "correctness-reviewer"])
            elif cat in ("test_gap", "missing_test", "vacuous_test"):
                selected.update(["test-falsifier", "correctness-reviewer"])
            elif cat in ("simplicity", "complexity", "dead_code"):
                selected.update(["simplicity-reviewer", "correctness-reviewer"])
            else:
                selected.update(["correctness-reviewer", "test-falsifier"])

        # Filter against available original roles or known reviewer roles
        target_roles = [r for r in original_roles if r in selected]
        if not target_roles:
            target_roles = list(selected)
        return sorted(list(set(target_roles)))
