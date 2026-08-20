#!/usr/bin/env python3
"""
test_interrupted_recovery_gaps.py

Reproduces pre-implementation gaps in operational resilience:
1. Interrupted implementation losing repo delta attribution on restart / rerun.
2. Concurrent mutation workflows lacking repository locks.
3. Post-execution crash leading to blind replay attempts of bounded actions.
4. Partial reviewer progress lost on crash.
5. Inability to cancel active in-flight tasks cleanly without code destruction.
"""

import json
import os
from pathlib import Path
import shutil
import tempfile
import pytest

from src.control_plane.agent_execution import AgentBackend, AgentExecutionResult
from src.control_plane.evidence_ledger import EvidenceLedger
from src.control_plane.executor import AuthorityExecutor, ExecutionReceipt, ExecutionResult, ExecutorRegistry
from src.control_plane.git_baseline import capture_baseline, capture_delta
from src.control_plane.human_boundary import HumanLifecycleManager, HumanDecisionRecord
from src.control_plane.orchestrator import GovernedTaskOrchestrator, OrchestrationConfig
from src.control_plane.proposed_action import ProposedAction
from src.control_plane.task_spec import TaskSpec


def _init_git_repo(path: Path) -> None:
    import subprocess
    subprocess.run(["git", "init"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(path), check=True, capture_output=True)
    (path / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(path), check=True, capture_output=True)


class MockInterruptedAgentBackend(AgentBackend):
    def __init__(self, mutate_fn=None, crash_after_mutation=False):
        self.mutate_fn = mutate_fn
        self.crash_after_mutation = crash_after_mutation
        self.invocations = 0

    def is_available(self) -> bool:
        return True

    def execute(self, task, cwd, role="implementation", **kwargs):
        self.invocations += 1
        if self.mutate_fn:
            self.mutate_fn(Path(cwd))
        if self.crash_after_mutation:
            raise KeyboardInterrupt("Simulated process crash / kill during implementation")
        return AgentExecutionResult(
            agent_id="mock_backend",
            role=role,
            command="mock",
            exit_code=0,
            stdout="Implemented successfully",
            stderr="",
            duration_seconds=0.1,
            success=True,
        )


def test_gap_interrupted_implementation_resets_baseline_and_loses_delta(tmp_path):
    """
    GAP 1: If implementation crashes after writing code to disk, currently resuming
    or rerunning re-baselines the repo, treating the task's own changes as pre-existing,
    resulting in an empty diff during review!
    """
    _init_git_repo(tmp_path)

    def write_change(repo_dir: Path):
        (repo_dir / "feature.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")

    spec = TaskSpec(
        task_id="TASK-GAP-001",
        repository=tmp_path.name,
        objective="Add hello world feature",
    )

    # First run crashes mid-way after modifying the disk
    backend = MockInterruptedAgentBackend(mutate_fn=write_change, crash_after_mutation=True)
    orch = GovernedTaskOrchestrator(target_repo=tmp_path, config=OrchestrationConfig(custom_backend=backend))

    with pytest.raises(KeyboardInterrupt):
        orch.run(spec)

    # Verify the code was indeed written to the repo
    assert (tmp_path / "feature.py").exists()

    # Now verify that without recovery reconciliation, running again recaptures baseline
    # and thinks the delta is empty:
    backend2 = MockInterruptedAgentBackend(mutate_fn=None, crash_after_mutation=False)
    orch2 = GovernedTaskOrchestrator(target_repo=tmp_path, config=OrchestrationConfig(custom_backend=backend2))
    
    # In current main, run() recaptures baseline and wipes out the diff attribution
    res2 = orch2.run(spec)
    assert res2.initial_delta is not None
    # Current gap: initial_delta is EMPTY because baseline included feature.py!
    assert res2.initial_delta.is_empty is True
    assert res2.initial_delta.diff_content == ""


def test_gap_missing_repository_mutation_lock(tmp_path):
    """
    GAP 2: HowlPlane currently has no repository-level lock, allowing two concurrent
    tasks to mutate the same workspace simultaneously.
    """
    _init_git_repo(tmp_path)

    spec_a = TaskSpec(task_id="TASK-GAP-002A", repository=tmp_path.name, objective="Feature A")
    spec_b = TaskSpec(task_id="TASK-GAP-002B", repository=tmp_path.name, objective="Feature B")

    backend_a = MockInterruptedAgentBackend(
        mutate_fn=lambda p: (p / "a.txt").write_text("a", encoding="utf-8")
    )
    backend_b = MockInterruptedAgentBackend(
        mutate_fn=lambda p: (p / "b.txt").write_text("b", encoding="utf-8")
    )

    orch_a = GovernedTaskOrchestrator(target_repo=tmp_path, config=OrchestrationConfig(custom_backend=backend_a))
    orch_b = GovernedTaskOrchestrator(target_repo=tmp_path, config=OrchestrationConfig(custom_backend=backend_b))

    # In current main, both run without checking any repository lock
    res_a = orch_a.run(spec_a)
    res_b = orch_b.run(spec_b)
    assert res_a.exit_code == 0
    assert res_b.exit_code == 0


def test_gap_howlchangeops_replayed_if_local_receipt_missing(tmp_path):
    """
    GAP 3: If HowlChangeOps executes successfully but the orchestrator dies before saving
    its local execution_receipt.json, resuming currently attempts to call execute() again!
    """
    _init_git_repo(tmp_path)

    run_dir = tmp_path / ".task_runs" / "TASK-GAP-003"
    run_dir.mkdir(parents=True, exist_ok=True)

    spec = TaskSpec(
        task_id="TASK-GAP-003",
        repository=tmp_path.name,
        objective="Create release candidate v1.0.0-rc.1",
        human_approval_requirements=["create_release_candidate"],
        current_state="awaiting_human",
    )
    spec.save_to_file(str(run_dir / "task.yaml"))

    decision_rec = HumanDecisionRecord(
        task_id="TASK-GAP-003",
        decision="approved",
        operator_source="cli",
        reason="Approved for release",
        boundary_triggers=["create_release_candidate"],
        changeops_decision_id="DEC-TEST-999",
    )
    (run_dir / "human_decision.json").write_text(decision_rec.to_json(), encoding="utf-8")

    class ReplayTrackingExecutor(AuthorityExecutor):
        def __init__(self):
            self.execute_calls = 0

        @property
        def name(self) -> str:
            return "howlchangeops"

        def is_available(self) -> bool:
            return True

        def supports_action(self, action_type: str) -> bool:
            return action_type == "create_release_candidate"

        def evaluate(self, action, repo_path, task_run_dir):
            return "REQUIRE_APPROVAL", "DEC-TEST-999", "Policy requires approval"

        def approve(self, decision_id, repo_path, task_run_dir):
            return True, "Approved"

        def execute(self, decision_id, repo_path, task_run_dir, action, task_id):
            self.execute_calls += 1
            receipt = ExecutionReceipt(
                task_id=task_id,
                executor=self.name,
                executor_version="0.2.0",
                decision_id=decision_id,
                action_type=action.action_type,
                repository=Path(repo_path).name,
                commit_sha="abcdef123456",
                status="success",
                executed_at="2026-08-20T12:00:00Z",
                verification_status="PASS",
                native_receipt={"action": action.action_type, "verification": "PASS"},
            )
            return ExecutionResult(
                executor_id=self.name,
                status="success",
                action_type=action.action_type,
                decision_id=decision_id,
                receipt=receipt,
                receipt_path=str(task_run_dir / "execution_receipt.json"),
                verification_status="PASS",
            )

        def verify_receipt(self, receipt, expected_action, expected_repo, expected_commit=None, run_dir=None):
            return True, None

    test_executor = ReplayTrackingExecutor()
    ExecutorRegistry.register(test_executor)

    # 1. First resume: execute() is called once
    res1 = HumanLifecycleManager.resume(target_repo=tmp_path, task_id="TASK-GAP-003")
    assert test_executor.execute_calls == 1
    assert res1.final_state == "complete"

    # 2. Simulate process crash before local execution_receipt.json was saved:
    # Remove local receipt and set state back to awaiting_human to simulate interrupted resume
    if (run_dir / "execution_receipt.json").exists():
        (run_dir / "execution_receipt.json").unlink()
    spec.current_state = "awaiting_human"
    spec.save_to_file(str(run_dir / "task.yaml"))

    # 3. In current main, resuming again calls execute() a SECOND time!
    res2 = HumanLifecycleManager.resume(target_repo=tmp_path, task_id="TASK-GAP-003")
    assert test_executor.execute_calls == 2, "Current main blindly replays execution when local receipt is absent"
