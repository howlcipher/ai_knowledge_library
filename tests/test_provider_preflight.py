import io
import json
import urllib.error
from unittest.mock import patch

from src.core.claude_code_backend import CLAUDE_CODE_MODEL
from src.core.provider_preflight import (
    PreflightResult,
    ollama_base_url,
    preflight_models,
)


def _tags_response(names):
    payload = json.dumps({"models": [{"name": n} for n in names]}).encode("utf8")
    response = io.BytesIO(payload)
    response.__enter__ = lambda *a: response
    response.__exit__ = lambda *a: False
    return response


def test_ollama_base_url_env_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_BASE", "http://box:11434/")
    assert ollama_base_url() == "http://box:11434"
    monkeypatch.delenv("OLLAMA_API_BASE")
    assert ollama_base_url() == "http://localhost:11434"


@patch("src.core.provider_preflight.litellm.completion")
@patch("src.core.provider_preflight.urllib.request.urlopen")
def test_healthy_ollama_model_passes(mock_urlopen, mock_completion):
    mock_urlopen.return_value = _tags_response(["qwen3:30b-instruct"])
    result = preflight_models(["ollama/qwen3:30b-instruct"])
    assert result.ok
    assert result.errors == []
    mock_completion.assert_called_once()
    assert mock_completion.call_args.kwargs["max_tokens"] == 1


@patch("src.core.provider_preflight.litellm.completion")
@patch("src.core.provider_preflight.urllib.request.urlopen")
def test_bare_tag_matches_latest(mock_urlopen, mock_completion):
    mock_urlopen.return_value = _tags_response(["qwen3:latest"])
    result = preflight_models(["ollama/qwen3"])
    assert result.ok


@patch("src.core.provider_preflight.litellm.completion")
@patch("src.core.provider_preflight.urllib.request.urlopen")
def test_dead_server_skips_generation(mock_urlopen, mock_completion):
    mock_urlopen.side_effect = urllib.error.URLError("connection refused")
    result = preflight_models(["ollama/qwen3:30b-instruct"])
    assert not result.ok
    assert "unreachable" in result.errors[0]
    assert "ollama serve" in result.errors[0]
    mock_completion.assert_not_called()


@patch("src.core.provider_preflight.litellm.completion")
@patch("src.core.provider_preflight.urllib.request.urlopen")
def test_missing_tag_names_available_models(mock_urlopen, mock_completion):
    mock_urlopen.return_value = _tags_response(["qwen2.5vl:7b"])
    result = preflight_models(["ollama/qwen3:30b-a3b"])
    assert not result.ok
    assert "qwen3:30b-a3b" in result.errors[0]
    assert "qwen2.5vl:7b" in result.errors[0]
    assert "ollama pull" in result.errors[0]
    mock_completion.assert_not_called()


@patch("src.core.provider_preflight.litellm.completion")
def test_non_ollama_model_only_runs_generation(mock_completion):
    result = preflight_models(["gemini/gemini-1.5-pro"])
    assert result.ok
    mock_completion.assert_called_once()


@patch("src.core.provider_preflight.litellm.completion")
def test_generation_failure_is_reported(mock_completion):
    mock_completion.side_effect = RuntimeError("no api key")
    result = preflight_models(["gemini/gemini-1.5-pro"])
    assert not result.ok
    assert "no api key" in result.errors[0]


@patch("src.core.provider_preflight.litellm.completion")
@patch("src.core.provider_preflight.urllib.request.urlopen")
def test_duplicate_models_checked_once_and_all_errors_collected(
    mock_urlopen, mock_completion
):
    mock_urlopen.side_effect = urllib.error.URLError("down")
    mock_completion.side_effect = RuntimeError("no api key")
    result = preflight_models(
        ["ollama/qwen3", "gemini/gemini-1.5-pro", "ollama/qwen3"]
    )
    assert not result.ok
    assert len(result.checked_models) == 2
    assert len(result.errors) == 2


@patch("src.core.orchestrator.Agent.generate_response")
@patch("src.core.provider_preflight.preflight_models")
def test_payload_loop_aborts_on_failed_preflight(mock_preflight, mock_generate):
    from src.core.orchestrator import Orchestrator

    mock_preflight.return_value = PreflightResult(
        ok=False, checked_models=["ollama/qwen3"], errors=["server down"]
    )
    orchestrator = Orchestrator()
    orchestrator.payload_cfg = dict(orchestrator.payload_cfg, enabled=True)
    result = orchestrator.run_payload_loop("Test query")
    assert result is None
    mock_preflight.assert_called_once()
    mock_generate.assert_not_called()


@patch("src.core.orchestrator.Agent.generate_response")
@patch("src.core.provider_preflight.preflight_models")
def test_payload_loop_skips_preflight_when_disabled(mock_preflight, mock_generate):
    from src.core.orchestrator import Orchestrator

    mock_generate.return_value = None  # first pass fails; only preflight matters
    orchestrator = Orchestrator()
    orchestrator.payload_cfg = dict(
        orchestrator.payload_cfg, enabled=True, preflight=False, max_attempts=1
    )
    orchestrator.run_payload_loop("Test query")
    mock_preflight.assert_not_called()


@patch("src.core.provider_preflight.shutil.which")
def test_claude_code_model_checks_cli_on_path(mock_which):
    mock_which.return_value = "/usr/bin/claude"
    result = preflight_models([CLAUDE_CODE_MODEL])
    assert result.ok
    assert result.errors == []
    mock_which.assert_called_once_with("claude")


@patch("src.core.provider_preflight.shutil.which")
def test_claude_code_model_missing_cli_fails(mock_which):
    mock_which.return_value = None
    result = preflight_models([CLAUDE_CODE_MODEL])
    assert not result.ok
    assert "claude" in result.errors[0].lower()
