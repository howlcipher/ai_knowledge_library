#!/usr/bin/env python3
"""
campaign_state.py

Durable campaign persistence for HowlPlane marathon dogfooding.
Tracks campaign identity, provider states, benchmark history, engineering tasks,
git commits / PRs / CI / merges, framework gaps, and resume points.
Guarantees atomic persistence across process boundaries and crashes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union

from src.control_plane.atomic_io import atomic_write_json, atomic_write_text, safe_load_json
from src.control_plane.task_spec import DataClassSerializationMixin

CAMPAIGN_STATE_SCHEMA_VERSION = "howlplane.marathon_dogfood_state/v1"

# Default local-only continuation budget: after all cloud providers are
# exhausted, at most this many consecutive local-eligible iterations run
# before the campaign stops cleanly (#58 Phase 13).
DEFAULT_LOCAL_ONLY_ITERATION_LIMIT = 10


def default_local_model_state() -> Dict[str, Any]:
    return {
        "provider": "local_ollama",
        "model": "qwen2.5-coder:7b-instruct",
        "context_length": 8192,
        "local_only_iterations": 0,
        "local_only_iteration_limit": DEFAULT_LOCAL_ONLY_ITERATION_LIMIT,
        "resource_guard_min_ram_gib": 8.0,
        "last_available_ram_gib": None,
        "success_count": 0,
        "failure_count": 0,
        "escalations": 0,
        "current_availability": "UNKNOWN",
    }


@dataclass
class GitIntegrationRecord(DataClassSerializationMixin):
    """Tracks a git commit, branch, PR, CI evaluation, and merge for an engineering task."""

    task_id: str
    target_repo: str
    branch: str
    commit_sha: str
    commit_message: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    ci_status: str = "passed"  # "passed", "failed", "pending", "simulated_green"
    merged: bool = True
    merged_at: Optional[str] = None
    schema: str = "howlplane.git_record/v1"


@dataclass
class DurableCampaignState(DataClassSerializationMixin):
    """
    Durable, serializable state of an autonomous dogfooding campaign.
    Persisted outside ephemeral task journals to allow reliable resume and audit.
    """

    campaign_id: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    north_star_objective: str = "Prompt -> Create -> Verify/Repair -> Usable Product"
    active_benchmark: Optional[str] = None
    active_engineering_task: Optional[str] = None
    # Persisted benchmark/task scope this campaign was actually asked to run.
    # `ai dogfood --resume <id>` restores exactly this scope rather than
    # silently expanding to the full default benchmark suite (#58 Phase 1).
    requested_benchmarks: List[str] = field(default_factory=list)
    scope_extensions: List[Dict[str, Any]] = field(default_factory=list)
    # Local (quota-free) model participation state (#58 Phase 15).
    local_model: Dict[str, Any] = field(default_factory=dict)
    benchmark_history: List[Dict[str, Any]] = field(default_factory=list)
    provider_states: Dict[str, str] = field(default_factory=dict)
    provider_invocations: Dict[str, int] = field(default_factory=dict)
    completed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    failed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    framework_gaps: List[Dict[str, Any]] = field(default_factory=list)
    git_records: List[Dict[str, Any]] = field(default_factory=list)
    reviewer_diversity_records: List[Dict[str, Any]] = field(default_factory=list)
    repair_cycles_total: int = 0
    stop_reason: str = "in_progress"
    next_action: str = "continue_benchmarks"
    total_duration_seconds: float = 0.0
    iterations_attempted: int = 0
    iterations_succeeded: int = 0
    iterations_failed: int = 0
    schema: str = CAMPAIGN_STATE_SCHEMA_VERSION

    def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def ensure_local_model_defaults(self) -> Dict[str, Any]:
        """Lazily populates `local_model` for campaigns created before #58."""
        if not self.local_model:
            self.local_model = default_local_model_state()
        return self.local_model

    def extend_benchmark_scope(self, additional_benchmarks: List[str]) -> List[str]:
        """
        Explicitly adds benchmarks to the persisted campaign scope. Returns the
        list of benchmarks actually added (already-present ones are no-ops).
        Recorded as a distinct scope-extension event so it's clear this was an
        explicit operator widening rather than an implicit resume expansion.
        """
        added = [b for b in additional_benchmarks if b not in self.requested_benchmarks]
        if added:
            self.requested_benchmarks = self.requested_benchmarks + added
            self.scope_extensions.append({
                "added": added,
                "at": datetime.now(timezone.utc).isoformat(),
            })
            self.update_timestamp()
        return added

    def record_local_success(self, ram_gib: Optional[float] = None) -> None:
        lm = self.ensure_local_model_defaults()
        lm["success_count"] = lm.get("success_count", 0) + 1
        if ram_gib is not None:
            lm["last_available_ram_gib"] = ram_gib
        self.update_timestamp()

    def record_local_failure(self, ram_gib: Optional[float] = None) -> None:
        lm = self.ensure_local_model_defaults()
        lm["failure_count"] = lm.get("failure_count", 0) + 1
        if ram_gib is not None:
            lm["last_available_ram_gib"] = ram_gib
        self.update_timestamp()

    def record_local_escalation(self) -> None:
        lm = self.ensure_local_model_defaults()
        lm["escalations"] = lm.get("escalations", 0) + 1
        self.update_timestamp()

    def increment_local_only_iteration(self) -> int:
        """Increments and returns the consecutive local-only continuation counter."""
        lm = self.ensure_local_model_defaults()
        lm["local_only_iterations"] = lm.get("local_only_iterations", 0) + 1
        self.update_timestamp()
        return lm["local_only_iterations"]

    def reset_local_only_iterations(self) -> None:
        """Resets the counter once cloud capacity is available again (not on local success)."""
        lm = self.ensure_local_model_defaults()
        lm["local_only_iterations"] = 0
        self.update_timestamp()

    def local_only_budget_reached(self) -> bool:
        lm = self.ensure_local_model_defaults()
        return lm.get("local_only_iterations", 0) >= lm.get("local_only_iteration_limit", DEFAULT_LOCAL_ONLY_ITERATION_LIMIT)

    def record_provider_invocation(self, agent_id: str) -> None:
        self.provider_invocations[agent_id] = self.provider_invocations.get(agent_id, 0) + 1
        self.update_timestamp()

    def record_benchmark_result(self, result_dict: Dict[str, Any]) -> None:
        self.benchmark_history.append(result_dict)
        self.iterations_attempted = len(self.benchmark_history)
        self.iterations_succeeded = sum(1 for r in self.benchmark_history if r.get("success", False))
        self.iterations_failed = self.iterations_attempted - self.iterations_succeeded
        self.repair_cycles_total += result_dict.get("repair_cycles", 0)
        self.update_timestamp()

    def record_task_completed(self, task_dict: Dict[str, Any]) -> None:
        self.completed_tasks.append(task_dict)
        self.update_timestamp()

    def record_task_failed(self, task_dict: Dict[str, Any]) -> None:
        self.failed_tasks.append(task_dict)
        self.update_timestamp()

    def record_framework_gap(self, gap_dict: Dict[str, Any]) -> None:
        # Avoid duplicate gaps by code
        code = gap_dict.get("code")
        if not any(g.get("code") == code for g in self.framework_gaps):
            self.framework_gaps.append(gap_dict)
            self.update_timestamp()

    def record_git_integration(self, git_rec: Dict[str, Any]) -> None:
        self.git_records.append(git_rec)
        self.update_timestamp()

    def save(self, run_dir: Union[str, Path]) -> Path:
        """Atomically saves campaign state and markdown report to directory."""
        target_dir = Path(run_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        self.update_timestamp()
        state_file = target_dir / "campaign_state.json"
        atomic_write_json(state_file, self.to_dict())
        summary_file = target_dir / "campaign_summary.md"
        atomic_write_text(summary_file, self.render_markdown())
        return state_file

    @classmethod
    def load(cls, run_dir: Union[str, Path]) -> "DurableCampaignState":
        target_dir = Path(run_dir).resolve()
        state_file = target_dir / "campaign_state.json"
        if not state_file.is_file():
            raise FileNotFoundError(f"Campaign state file not found at {state_file}")
        data = safe_load_json(state_file)
        return cls.from_dict(data)

    def render_markdown(self) -> str:
        lines = [
            f"# HowlPlane Marathon Dogfooding Report: `{self.campaign_id}`",
            "",
            f"- **Schema:** `{self.schema}`",
            f"- **Started At:** `{self.started_at}`",
            f"- **Updated At:** `{self.updated_at}`",
            f"- **Stop Reason:** `{self.stop_reason}`",
            f"- **Total Duration:** `{self.total_duration_seconds}s`",
            f"- **Iterations:** {self.iterations_succeeded}/{self.iterations_attempted} succeeded ({self.iterations_failed} failed)",
            f"- **Total Repair Cycles:** {self.repair_cycles_total}",
            f"- **Next Action:** `{self.next_action}`",
            f"- **Requested Benchmark Scope:** `{', '.join(self.requested_benchmarks) or 'N/A'}`",
            "",
            "## Provider Status & Invocations",
            "",
            "| Provider | Live State | Invocations |",
            "| --- | --- | --- |",
        ]
        all_providers = sorted(set(list(self.provider_states.keys()) + list(self.provider_invocations.keys())))
        for p in all_providers:
            st = self.provider_states.get(p, "UNKNOWN")
            inv = self.provider_invocations.get(p, 0)
            lines.append(f"| `{p}` | `{st}` | {inv} |")

        lines.extend([
            "",
            "## Benchmarks & Products Created",
            "",
            "| Benchmark | Product | Success | Checks | Repairs | Duration | Provider | Bundle Path |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ])
        for b in self.benchmark_history:
            mark = "✓ PASS" if b.get("success") else "✗ FAIL"
            checks = f"{b.get('passed_checks', 0)}/{b.get('total_checks', 0)}"
            bpath = b.get("bundle_path") or "N/A"
            lines.append(
                f"| {b.get('benchmark_id')} | {b.get('product_name')} | {mark} | {checks} | "
                f"{b.get('repair_cycles', 0)} | {b.get('duration_seconds', 0)}s | "
                f"`{b.get('implementing_provider', 'unknown')}` | `{bpath}` |"
            )

        if self.local_model:
            lm = self.local_model
            lines.extend([
                "",
                "## Local Model Participation",
                "",
                f"- **Provider/Model:** `{lm.get('provider')}` / `{lm.get('model')}`",
                f"- **Context Length:** {lm.get('context_length')}",
                f"- **Local Success/Failure:** {lm.get('success_count', 0)}/{lm.get('failure_count', 0)}",
                f"- **Escalations to Cloud:** {lm.get('escalations', 0)}",
                f"- **Local-Only Continuation:** {lm.get('local_only_iterations', 0)}/{lm.get('local_only_iteration_limit')}",
                f"- **Last Observed Available RAM:** {lm.get('last_available_ram_gib')} GiB",
                f"- **Current Availability:** `{lm.get('current_availability')}`",
            ])

        if self.framework_gaps:
            lines.extend([
                "",
                "## Framework & Runtime Gaps Discovered",
                "",
                "| Gap Code | Target Component | Description | Impact |",
                "| --- | --- | --- | --- |",
            ])
            for g in self.framework_gaps:
                lines.append(
                    f"| `{g.get('code')}` | `{g.get('target_component')}` | {g.get('required_behavior')} | `{g.get('impact')}` |"
                )

        if self.completed_tasks or self.failed_tasks:
            lines.extend([
                "",
                "## Governed Engineering Tasks",
                "",
                "| Task ID | Status | Objective | Provider | Remediations |",
                "| --- | --- | --- | --- | --- |",
            ])
            for t in self.completed_tasks:
                lines.append(
                    f"| `{t.get('task_id')}` | ✓ COMPLETED | {t.get('objective', '')[:50]} | `{t.get('provider')}` | {t.get('remediations', 0)} |"
                )
            for t in self.failed_tasks:
                lines.append(
                    f"| `{t.get('task_id')}` | ✗ FAILED | {t.get('objective', '')[:50]} | `{t.get('provider')}` | {t.get('error', '')[:30]} |"
                )

        if self.git_records:
            lines.extend([
                "",
                "## Git Commits, Pull Requests & Merges",
                "",
                "| Task ID | Repo | Branch | Commit SHA | PR | CI Status | Merged |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ])
            for gr in self.git_records:
                pr_str = f"#{gr.get('pr_number')}" if gr.get("pr_number") else "N/A"
                merged_str = "✓ MERGED" if gr.get("merged") else "PENDING"
                lines.append(
                    f"| `{gr.get('task_id')}` | `{gr.get('target_repo')}` | `{gr.get('branch')}` | `{gr.get('commit_sha', '')[:8]}` | {pr_str} | `{gr.get('ci_status')}` | {merged_str} |"
                )

        if self.reviewer_diversity_records:
            lines.extend([
                "",
                "## Reviewer Diversity Verification",
                "",
                "| Task/Product | Implementer | Reviewers | Independent Diversity Achieved |",
                "| --- | --- | --- | --- |",
            ])
            for rd in self.reviewer_diversity_records:
                div_str = "✓ YES" if rd.get("diversity_achieved") else "⚠ REDUCED (Single Provider)"
                revs = ", ".join(f"{k}:{v}" for k, v in rd.get("reviewers", {}).items())
                lines.append(
                    f"| `{rd.get('target')}` | `{rd.get('implementer')}` | `{revs}` | {div_str} |"
                )

        lines.extend([
            "",
            "## Resume Command",
            "",
            "To resume or continue this dogfood campaign with updated quotas:",
            "```bash",
            f"ai dogfood --resume {self.campaign_id}",
            "```",
            "",
        ])
        return "\n".join(lines)
