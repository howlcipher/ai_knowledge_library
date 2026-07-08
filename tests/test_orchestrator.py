import pytest
from unittest.mock import patch, MagicMock
from tools.orchestrator import Agent, Orchestrator

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
    
    with patch("tools.orchestrator.log_telemetry") as mock_log:
        response = agent.generate_response("Hello", context="Some context")
        assert response == "Mocked answer"
        mock_log.assert_called_once()
        args, kwargs = mock_log.call_args
        assert kwargs["prompt_tokens"] == 10

def test_human_proxy_no_command():
    orchestrator = Orchestrator()
    # Should automatically return True since no ```bash is present
    result = orchestrator.human_proxy_intercept("Here is a normal response without commands.")
    assert result is True

@patch("builtins.input", return_value="y")
def test_human_proxy_authorized(mock_input):
    orchestrator = Orchestrator()
    result = orchestrator.human_proxy_intercept("Here is a command:\n```bash\necho hello\n```")
    assert result is True

@patch("builtins.input", return_value="n")
def test_human_proxy_rejected(mock_input):
    orchestrator = Orchestrator()
    result = orchestrator.human_proxy_intercept("Here is a command:\n```bash\necho hello\n```")
    assert result is False

@patch("tools.orchestrator.Agent.generate_response")
@patch("tools.orchestrator.Orchestrator.human_proxy_intercept", return_value=True)
def test_orchestrator_run_loop_approved_immediately(mock_proxy, mock_generate):
    orchestrator = Orchestrator()
    
    # Setup mocks
    # First call is Researcher, second is QA
    mock_generate.side_effect = ["Here is my research draft", "APPROVED"]
    
    orchestrator.run_loop("Test query")
    
    # Should have called Researcher and QA exactly once
    assert mock_generate.call_count == 2
    mock_proxy.assert_called_once()

@patch("tools.orchestrator.Agent.generate_response")
@patch("tools.orchestrator.Orchestrator.human_proxy_intercept", return_value=True)
def test_orchestrator_run_loop_rejected_then_approved(mock_proxy, mock_generate):
    orchestrator = Orchestrator()
    
    # First iteration: Researcher -> QA rejects
    # Second iteration: Researcher -> QA approves
    mock_generate.side_effect = [
        "First draft", "REJECTED. Fix it.",
        "Second draft", "APPROVED"
    ]
    
    orchestrator.run_loop("Test query")
    
    assert mock_generate.call_count == 4
    mock_proxy.assert_called_once()

def test_main(monkeypatch):
    import sys
    from tools.orchestrator import main
    
    with patch("tools.orchestrator.Orchestrator.run_loop") as mock_run:
        monkeypatch.setattr(sys, "argv", ["orchestrator.py", "What is AI?"])
        main()
        mock_run.assert_called_once_with("What is AI?")
