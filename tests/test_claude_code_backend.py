import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src.core.claude_code_backend import CLAUDE_CODE_MODEL, ClaudeCodeAgent


def _mock_completed_process(stdout="", stderr="", returncode=0):
    proc = MagicMock()
    proc.stdout = stdout
    proc.stderr = stderr
    proc.returncode = returncode
    return proc


def test_claude_code_model_sentinel():
    assert CLAUDE_CODE_MODEL == "claude_code"


def test_generate_response_success():
    agent = ClaudeCodeAgent("Tier1", "You are a judge.")
    mock_proc = _mock_completed_process(
        stdout='{"type": "result", "subtype": "success", "is_error": false, "result": "Hello from Claude Code"}'
    )
    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        response = agent.generate_response("Say hello")
        assert response.content == "Hello from Claude Code"
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert cmd[0] == "claude"
        assert "-p" in cmd
        assert "--output-format" in cmd
        assert "json" in cmd
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True


def test_generate_response_includes_system_prompt_and_context():
    agent = ClaudeCodeAgent("Tier1", "SYSTEM_PROMPT_MARKER")
    mock_proc = _mock_completed_process(stdout='{"is_error": false, "result": "ok"}')
    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        agent.generate_response("USER_PROMPT_MARKER", context="CONTEXT_MARKER")
        args, _ = mock_run.call_args
        cmd = args[0]
        full_prompt = cmd[cmd.index("-p") + 1]
        assert "SYSTEM_PROMPT_MARKER" in full_prompt
        assert "USER_PROMPT_MARKER" in full_prompt
        assert "CONTEXT_MARKER" in full_prompt


def test_generate_response_is_error_returns_none_by_default():
    agent = ClaudeCodeAgent("Tier1", "prompt")
    mock_proc = _mock_completed_process(
        stdout='{"is_error": true, "result": "something went wrong"}'
    )
    with patch("subprocess.run", return_value=mock_proc):
        assert agent.generate_response("hi") is None


def test_generate_response_is_error_raises_when_requested():
    agent = ClaudeCodeAgent("Tier1", "prompt")
    mock_proc = _mock_completed_process(
        stdout='{"is_error": true, "result": "something went wrong"}'
    )
    with patch("subprocess.run", return_value=mock_proc):
        with pytest.raises(RuntimeError):
            agent.generate_response("hi", raise_errors=True)


def test_generate_response_nonzero_exit_raises_when_requested():
    agent = ClaudeCodeAgent("Tier1", "prompt")
    mock_proc = _mock_completed_process(stdout="", stderr="boom", returncode=1)
    with patch("subprocess.run", return_value=mock_proc):
        with pytest.raises(RuntimeError):
            agent.generate_response("hi", raise_errors=True)


def test_generate_response_malformed_json_returns_none_by_default():
    agent = ClaudeCodeAgent("Tier1", "prompt")
    mock_proc = _mock_completed_process(stdout="not json")
    with patch("subprocess.run", return_value=mock_proc):
        assert agent.generate_response("hi") is None


def test_generate_response_timeout_raises_when_requested():
    agent = ClaudeCodeAgent("Tier1", "prompt", timeout=5)
    with patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=5),
    ):
        with pytest.raises(subprocess.TimeoutExpired):
            agent.generate_response("hi", raise_errors=True)


def test_generate_response_cli_not_found_returns_none_by_default():
    agent = ClaudeCodeAgent("Tier1", "prompt")
    with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
        assert agent.generate_response("hi") is None


def test_generate_response_folds_response_format_schema_into_prompt():
    agent = ClaudeCodeAgent(
        "Tier1",
        "prompt",
        response_format={
            "json_schema": {
                "schema": {"type": "object", "properties": {"x": {"type": "string"}}}
            }
        },
    )
    mock_proc = _mock_completed_process(stdout='{"is_error": false, "result": "{}"}')
    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        agent.generate_response("hi")
        args, _ = mock_run.call_args
        cmd = args[0]
        full_prompt = cmd[cmd.index("-p") + 1]
        assert "JSON schema" in full_prompt
        assert '"type": "object"' in full_prompt
