import pytest
import json
from unittest.mock import patch, MagicMock
from src.core.orchestrator import Agent, Orchestrator, tier_setting

class MockMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

class MockToolCall:
    def __init__(self, name, arguments):
        class Function:
            def __init__(self, n, a):
                self.name = n
                self.arguments = a
        self.function = Function(name, arguments)

def test_agent_initialization():
    agent = Agent("TestAgent", "You are a test.", "gemini/gemini-1.5-pro")
    assert agent.name == "TestAgent"
    assert agent.system_prompt == "You are a test."

@patch("litellm.completion_cost")
@patch("litellm.completion")
def test_agent_generate_response(mock_completion, mock_cost):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked answer"))]
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    mock_response.model = "gemini/gemini-1.5-pro"
    mock_completion.return_value = mock_response
    mock_cost.return_value = 0.05
    
    agent = Agent("TestAgent", "You are a test.", "gemini/gemini-1.5-pro")
    
    with patch("src.core.orchestrator.log_telemetry") as mock_log:
        response = agent.generate_response("Hello", context="Some context")
        assert response.content == "Mocked answer"
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert kwargs["prompt_tokens"] == 10

@patch("litellm.completion_cost", return_value=0.0)
@patch("litellm.completion")
def test_agent_timeout_passed_to_litellm(mock_completion, mock_cost):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
    mock_response.usage.prompt_tokens = 1
    mock_response.usage.completion_tokens = 1
    mock_response.usage.total_tokens = 2
    mock_completion.return_value = mock_response

    agent = Agent("TestAgent", "You are a test.", "ollama/qwen3", timeout=1800.0)
    with patch("src.core.orchestrator.log_telemetry"):
        agent.generate_response("Hello")
    assert mock_completion.call_args.kwargs["timeout"] == 1800.0


@patch("litellm.completion_cost", return_value=0.0)
@patch("litellm.completion")
def test_agent_without_timeout_omits_kwarg(mock_completion, mock_cost):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
    mock_response.usage.prompt_tokens = 1
    mock_response.usage.completion_tokens = 1
    mock_response.usage.total_tokens = 2
    mock_completion.return_value = mock_response

    agent = Agent("TestAgent", "You are a test.", "ollama/qwen3")
    with patch("src.core.orchestrator.log_telemetry"):
        agent.generate_response("Hello")
    assert "timeout" not in mock_completion.call_args.kwargs


def test_tier_setting_fallbacks():
    overrides = {"tier_1": 900.0, "tier_2": 0.0}
    assert tier_setting(overrides, 1, 600.0) == 900.0
    # Zero and missing overrides both fall back to the default.
    assert tier_setting(overrides, 2, 600.0) == 600.0
    assert tier_setting(overrides, 3, 600.0) == 600.0
    assert tier_setting(None, 1, 600.0) == 600.0
    # Same helper backs per tier models: empty string falls back too.
    assert tier_setting({"tier_1": ""}, 1, "default-model") == "default-model"


def test_human_proxy_no_command():
    orchestrator = Orchestrator()
    result = orchestrator.human_proxy_intercept(None)
    assert result is True

@patch("builtins.input", return_value="y")
def test_human_proxy_authorized(mock_input):
    orchestrator = Orchestrator()
    tool_calls = [MockToolCall("execute_bash_command", json.dumps({"command": "echo hello"}))]
    result = orchestrator.human_proxy_intercept(tool_calls)
    assert result is True

@patch("builtins.input", return_value="n")
def test_human_proxy_rejected(mock_input):
    orchestrator = Orchestrator()
    tool_calls = [MockToolCall("execute_bash_command", json.dumps({"command": "echo hello"}))]
    result = orchestrator.human_proxy_intercept(tool_calls)
    assert result is False

@patch("src.core.orchestrator.Agent.generate_response")
@patch("src.core.orchestrator.Orchestrator.human_proxy_intercept", return_value=True)
def test_orchestrator_run_loop_approved_immediately(mock_proxy, mock_generate):
    orchestrator = Orchestrator()
    
    mock_generate.side_effect = [
        MockMessage("Here is my research draft"), 
        MockMessage("APPROVED"),
        MockMessage("Humanized draft")
    ]
    
    orchestrator.run_loop("Test query")
    
    assert mock_generate.call_count == 3
    mock_proxy.assert_called_once()

@patch("src.core.orchestrator.Agent.generate_response")
@patch("src.core.orchestrator.Orchestrator.human_proxy_intercept", return_value=True)
def test_orchestrator_run_loop_rejected_then_approved(mock_proxy, mock_generate):
    orchestrator = Orchestrator()
    
    mock_generate.side_effect = [
        MockMessage("First draft"), MockMessage("REJECTED. Fix it."),
        MockMessage("Second draft"), MockMessage("APPROVED"),
        MockMessage("Humanized second draft")
    ]
    
    orchestrator.run_loop("Test query")
    
    assert mock_generate.call_count == 5
    mock_proxy.assert_called_once()

def test_main(monkeypatch):
    import sys
    from src.core.orchestrator import main
    
    with patch("src.core.orchestrator.Orchestrator.run_loop") as mock_run:
        monkeypatch.setattr(sys, "argv", ["orchestrator.py", "What is AI?"])
        main()
        mock_run.assert_called_once_with("What is AI?")
