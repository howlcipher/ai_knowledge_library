"""
test_agent_execution.py

Unit and integration tests for normalized agent execution abstraction.
"""

from src.control_plane.agent_execution import (
    AgentBackendRegistry,
    AgentExecutionResult,
    ClaudeCodeBackend,
    CodexBackend,
    FakeAgentBackend,
    SubprocessAgentBackend,
)
from src.control_plane.task_spec import TaskSpec


def test_agent_execution_result_serialization():
    res = AgentExecutionResult(
        agent_id="codex",
        role="implementation",
        command="codex 'Fix bug'",
        exit_code=0,
        stdout="Fixed issue",
        stderr="",
        duration_seconds=1.23,
        success=True,
        metadata={"tokens": 150},
    )
    data = res.to_dict()
    assert data["agent_id"] == "codex"
    assert data["success"] is True
    assert data["duration_seconds"] == 1.23

    restored = AgentExecutionResult.from_dict(data)
    assert restored.agent_id == res.agent_id
    assert restored.exit_code == 0
    assert restored.metadata["tokens"] == 150

    json_str = res.to_json()
    assert '"agent_id": "codex"' in json_str
    restored_json = AgentExecutionResult.from_json(json_str)
    assert restored_json.command == res.command


def test_fake_agent_backend_execution(tmp_path):
    spec = TaskSpec(
        task_id="TASK-EXEC-001",
        repository="repo_sample",
        objective="Create a hello.py file for testing",
    )

    def side_effect(task, cwd, prompt):
        (cwd / "hello.py").write_text("print('hello')", encoding="utf-8")

    backend = FakeAgentBackend(
        agent_id="fake_coder",
        default_exit_code=0,
        default_stdout="Created hello.py",
        side_effect=side_effect,
    )

    res = backend.execute(spec, cwd=tmp_path, role="implementation")
    assert res.success is True
    assert res.exit_code == 0
    assert res.stdout == "Created hello.py"
    assert (tmp_path / "hello.py").read_text(encoding="utf-8") == "print('hello')"
    assert len(backend.executed_calls) == 1
    assert backend.executed_calls[0]["task_id"] == spec.task_id


def test_fake_agent_backend_failure(tmp_path):
    spec = TaskSpec(
        task_id="TASK-002",
        repository="test_repo",
        objective="Fail intentionally",
    )
    backend = FakeAgentBackend(
        agent_id="fake_failing",
        default_exit_code=1,
        default_stdout="",
        default_stderr="Compilation failed",
    )
    res = backend.execute(spec, cwd=tmp_path, role="implementation")
    assert res.success is False
    assert res.exit_code == 1
    assert "Compilation failed" in res.stderr
    assert res.error_message == "Exit code 1"


def test_backend_registry():
    claude = AgentBackendRegistry.get_backend("claude_code")
    assert isinstance(claude, ClaudeCodeBackend)

    codex = AgentBackendRegistry.get_backend("codex")
    assert isinstance(codex, CodexBackend)

    custom = FakeAgentBackend("custom")
    retrieved = AgentBackendRegistry.get_backend("claude_code", custom_backend=custom)
    assert retrieved is custom


def test_subprocess_agent_backend_unavailable(tmp_path):
    spec = TaskSpec(
        task_id="TASK-003",
        repository="test_repo",
        objective="Run non-existent agent",
    )
    backend = SubprocessAgentBackend("nonexistent_binary_xyz_123", "nonexistent_binary_xyz_123")
    assert backend.is_available() is False

    res = backend.execute(spec, cwd=tmp_path)
    assert res.success is False
    assert res.exit_code == 127
    assert "not installed" in res.stderr
