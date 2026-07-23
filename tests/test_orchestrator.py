import pytest
import json
from unittest.mock import patch, MagicMock
from src.core.orchestrator import Agent, Orchestrator, build_tier_agent, tier_setting
from src.core.provider_preflight import PreflightResult

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


@patch("litellm.completion_cost", return_value=0.0)
@patch("litellm.completion")
def test_agent_response_format_passed_to_litellm(mock_completion, mock_cost):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
    mock_response.usage.prompt_tokens = 1
    mock_response.usage.completion_tokens = 1
    mock_response.usage.total_tokens = 2
    mock_completion.return_value = mock_response

    rf = {"type": "json_schema", "json_schema": {"name": "x", "schema": {}}}
    agent = Agent("TestAgent", "You are a test.", "ollama/qwen3", response_format=rf)
    with patch("src.core.orchestrator.log_telemetry"):
        agent.generate_response("Hello")
    assert mock_completion.call_args.kwargs["response_format"] == rf


@patch("litellm.completion_cost", return_value=0.0)
@patch("litellm.completion")
def test_agent_without_response_format_omits_kwarg(mock_completion, mock_cost):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]
    mock_response.usage.prompt_tokens = 1
    mock_response.usage.completion_tokens = 1
    mock_response.usage.total_tokens = 2
    mock_completion.return_value = mock_response

    agent = Agent("TestAgent", "You are a test.", "ollama/qwen3")
    with patch("src.core.orchestrator.log_telemetry"):
        agent.generate_response("Hello")
    assert "response_format" not in mock_completion.call_args.kwargs


def test_tier_setting_fallbacks():
    overrides = {"tier_1": 900.0, "tier_2": 0.0}
    assert tier_setting(overrides, 1, 600.0) == 900.0
    # Zero and missing overrides both fall back to the default.
    assert tier_setting(overrides, 2, 600.0) == 600.0
    assert tier_setting(overrides, 3, 600.0) == 600.0
    assert tier_setting(None, 1, 600.0) == 600.0
    # Same helper backs per tier models: empty string falls back too.
    assert tier_setting({"tier_1": ""}, 1, "default-model") == "default-model"


def test_human_proxy_no_command(orchestrator_factory):
    orchestrator = orchestrator_factory()
    result = orchestrator.human_proxy_intercept(None)
    assert result is True

@patch("builtins.input", return_value="y")
def test_human_proxy_authorized(mock_input, orchestrator_factory):
    orchestrator = orchestrator_factory()
    tool_calls = [MockToolCall("execute_bash_command", json.dumps({"command": "echo hello"}))]
    result = orchestrator.human_proxy_intercept(tool_calls)
    assert result is True

@patch("builtins.input", return_value="n")
def test_human_proxy_rejected(mock_input, orchestrator_factory):
    orchestrator = orchestrator_factory()
    tool_calls = [MockToolCall("execute_bash_command", json.dumps({"command": "echo hello"}))]
    result = orchestrator.human_proxy_intercept(tool_calls)
    assert result is False

@patch("src.core.provider_preflight.preflight_models")
@patch("src.core.orchestrator.Agent.generate_response")
@patch("src.core.orchestrator.Orchestrator.human_proxy_intercept", return_value=True)
def test_orchestrator_run_loop_approved_immediately(mock_proxy, mock_generate, mock_preflight, orchestrator_factory):
    # run_loop preflights the provider before the multi-agent loop (item 33);
    # stub it out so this test exercises the approve/reject flow, not a real
    # network check against whatever provider config/settings.yaml points at.
    mock_preflight.return_value = PreflightResult(ok=True, checked_models=["stub"])
    orchestrator = orchestrator_factory()

    mock_generate.side_effect = [
        MockMessage("Here is my research draft"),
        MockMessage("APPROVED"),
        MockMessage("Humanized draft")
    ]

    orchestrator.run_loop("Test query")

    assert mock_generate.call_count == 3
    mock_proxy.assert_called_once()

@patch("src.core.provider_preflight.preflight_models")
@patch("src.core.orchestrator.Agent.generate_response")
@patch("src.core.orchestrator.Orchestrator.human_proxy_intercept", return_value=True)
def test_orchestrator_run_loop_rejected_then_approved(mock_proxy, mock_generate, mock_preflight, orchestrator_factory):
    mock_preflight.return_value = PreflightResult(ok=True, checked_models=["stub"])
    orchestrator = orchestrator_factory()

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


def test_build_tier_agent_returns_plain_agent_for_litellm_model():
    agent = build_tier_agent("Tier3", "prompt", "gemini/gemini-1.5-pro", timeout=30)
    assert isinstance(agent, Agent)
    assert agent.model == "gemini/gemini-1.5-pro"
    assert agent.timeout == 30


def test_build_tier_agent_returns_claude_code_agent_for_sentinel():
    from src.core.claude_code_backend import ClaudeCodeAgent

    agent = build_tier_agent("Tier1", "prompt", "claude_code", timeout=60)
    assert isinstance(agent, ClaudeCodeAgent)
    assert agent.model == "claude_code"
    assert agent.timeout == 60

def test_orchestrator_factory_provides_shutdown_callable(orchestrator_factory):
    orchestrator = orchestrator_factory()
    assert callable(orchestrator.shutdown)

@patch("src.core.mcp_client.SyncMCPClient")
def test_orchestrator_shutdown_calls_close_on_every_mcp_client(mock_sync_cls):
    created_clients = []

    def _new_client(*args, **kwargs):
        client = MagicMock()
        client.get_tools.return_value = []
        created_clients.append(client)
        return client

    mock_sync_cls.side_effect = _new_client

    orchestrator = Orchestrator()
    assert created_clients, "expected at least one MCP client to be constructed"
    orchestrator.shutdown()

    for client in created_clients:
        client.close.assert_called_once()
        # connect() must be bounded: a hanging/missing MCP server should
        # not be able to block Orchestrator construction forever.
        client.connect.assert_called_once_with(
            timeout=orchestrator.cfg.get("mcp_connect_timeout", 30.0)
        )
