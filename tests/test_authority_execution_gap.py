"""
test_authority_execution_gap.py

Deterministic reproduction tests for authority gap and false completion:
1. Proves that `ai work --execute` with a consequential action launches the
   unrestricted implementation backend BEFORE evaluating the human boundary.
2. Proves that `HumanLifecycleManager.resume()` marks a consequential task COMPLETE
   solely based on human approval, without any bounded execution or receipt.
"""

from pathlib import Path
import subprocess
import pytest

from src.control_plane.agent_execution import AgentBackend, AgentExecutionResult
from src.control_plane.evidence_ledger import EvidenceLedger
from src.control_plane.human_boundary import HumanLifecycleManager
from src.control_plane.orchestrator import GovernedTaskOrchestrator, OrchestrationConfig
from src.control_plane.task_spec import TaskSpec


class CountingMockBackend(AgentBackend):
    """Mock agent backend that records execution invocations."""

    def __init__(self):
        self.impl_invocations = 0
        self.total_invocations = 0
        self.executed_prompts = []

    def is_available(self) -> bool:
        return True

    def execute(
        self,
        task: TaskSpec,
        cwd: Path,
        role: str = "implementation",
        prompt_override: str = None,
        timeout_seconds: int = 600,
    ) -> AgentExecutionResult:
        self.total_invocations += 1
        if role == "implementation":
            self.impl_invocations += 1
        self.executed_prompts.append(prompt_override or "")
        return AgentExecutionResult(
            agent_id="counting_mock",
            role=role,
            command="mock",
            exit_code=0,
            stdout="Mock execution completed",
            stderr="",
            duration_seconds=0.1,
            success=True,
        )


def _init_git_repo(repo_path: Path) -> None:
    """Initializes a clean git repository."""
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "TestUser"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True)
    (repo_path / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=repo_path, check=True, capture_output=True)


def test_reproduce_consequential_action_reaches_implementation_agent_before_boundary(tmp_path: Path):
    """
    REPRODUCTION TEST 1:
    A task with a consequential action ('terraform apply') reaches the unrestricted
    implementation backend BEFORE any human authority decision is evaluated.
    """
    _init_git_repo(tmp_path)
    backend = CountingMockBackend()

    orchestrator = GovernedTaskOrchestrator(
        target_repo=tmp_path,
        config=OrchestrationConfig(
            custom_backend=backend,
            enable_howlframe_audit=False,
            record_evidence=False,
        ),
    )

    spec = TaskSpec(
        task_id="TASK-CONSEQ-01",
        repository=tmp_path.name,
        objective="Run terraform apply to update production infrastructure",
        task_class="infrastructure",
        risk_level="critical",
        human_approval_requirements=["infrastructure_apply"],
    )

    # In current buggy code, orchestrator.run launches the backend at Stage 4
    # before evaluating the boundary at Stage 7.
    res = orchestrator.run(spec, planned_actions=["terraform apply -auto-approve"])

    # PROOF OF BUG IN CURRENT MAIN: implementation backend was invoked (impl_invocations == 1)!
    # The authority model requires impl_invocations == 0 for consequential execution before approval.
    assert backend.impl_invocations == 1, "Demonstrates that current main executes implementation backend before human boundary"
    assert res.final_state == "awaiting_human"


def test_reproduce_approval_alone_mistaken_for_completion(tmp_path: Path):
    """
    REPRODUCTION TEST 2:
    An approved awaiting_human task transitions to COMPLETE in resume() without
    any bounded execution taking place or any execution receipt being validated.
    """
    _init_git_repo(tmp_path)
    run_dir = tmp_path / ".task_runs" / "TASK-CONSEQ-02"
    run_dir.mkdir(parents=True, exist_ok=True)

    spec = TaskSpec(
        task_id="TASK-CONSEQ-02",
        repository=tmp_path.name,
        objective="Apply database drop table and publish package",
        task_class="infrastructure",
        risk_level="critical",
        human_approval_requirements=["destructive_database_change", "package_publishing"],
        current_state="awaiting_human",
    )
    spec.save_to_file(str(run_dir / "task.yaml"))
    (run_dir / "diff.patch").write_text("", encoding="utf-8")

    # Operator approves the task
    HumanLifecycleManager.approve(
        target_repo=tmp_path,
        task_id="TASK-CONSEQ-02",
        reason="Operator approved plan",
    )

    # Operator resumes the task
    res = HumanLifecycleManager.resume(
        target_repo=tmp_path,
        task_id="TASK-CONSEQ-02",
    )

    # PROOF OF BUG IN CURRENT MAIN: res.final_state is 'complete' without any execution!
    # No receipt exists under .task_runs/TASK-CONSEQ-02/execution_receipt.json,
    # yet the task was marked COMPLETE.
    assert res.final_state == "complete", "Demonstrates that current main marks approved task complete without execution"
    assert not (run_dir / "execution_receipt.json").exists(), "No execution receipt exists, yet task completed"
