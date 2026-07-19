"""Tests for the transport retry layer (improvement #7): provider exceptions
are retried with backoff and surface as ProviderTransportError instead of
being swallowed into empty responses."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.orchestrator import Agent
from src.core.transport_retry import (
    ProviderTransportError,
    call_with_transport_retry,
)


class TestCallWithTransportRetry:
    def test_returns_result_on_first_success_without_sleeping(self):
        sleep = MagicMock()
        result = call_with_transport_retry(lambda: "ok", retries=2, sleep=sleep)
        assert result == "ok"
        sleep.assert_not_called()

    def test_retries_with_exponential_backoff_then_succeeds(self):
        sleep = MagicMock()
        fn = MagicMock(side_effect=[ConnectionError("refused"), TimeoutError("slow"), "ok"])
        result = call_with_transport_retry(fn, retries=2, backoff=2.0, sleep=sleep)
        assert result == "ok"
        assert fn.call_count == 3
        assert [c.args[0] for c in sleep.call_args_list] == [2.0, 4.0]

    def test_exhaustion_raises_with_all_attempt_errors(self):
        fn = MagicMock(side_effect=ConnectionError("connection refused"))
        with pytest.raises(ProviderTransportError) as exc_info:
            call_with_transport_retry(
                fn, retries=2, backoff=0.0, model="ollama/qwen3", sleep=MagicMock()
            )
        err = exc_info.value
        assert fn.call_count == 3
        assert err.model == "ollama/qwen3"
        assert len(err.attempt_errors) == 3
        assert all("connection refused" in e for e in err.attempt_errors)
        assert "3 attempts" in str(err)

    def test_zero_retries_means_single_attempt(self):
        sleep = MagicMock()
        fn = MagicMock(side_effect=ConnectionError("down"))
        with pytest.raises(ProviderTransportError) as exc_info:
            call_with_transport_retry(fn, retries=0, sleep=sleep)
        assert fn.call_count == 1
        sleep.assert_not_called()
        assert len(exc_info.value.attempt_errors) == 1


def make_llm_response(content="hello"):
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    response.usage.prompt_tokens = 1
    response.usage.completion_tokens = 1
    response.usage.total_tokens = 2
    return response


class TestAgentRaiseErrors:
    def test_raise_errors_propagates_provider_exception(self):
        agent = Agent("T", "prompt", "ollama/qwen3")
        with patch("litellm.completion", side_effect=ConnectionError("refused")):
            with pytest.raises(ConnectionError):
                agent.generate_response("hi", raise_errors=True)

    def test_default_still_swallows_provider_exception(self):
        agent = Agent("T", "prompt", "ollama/qwen3")
        with patch("litellm.completion", side_effect=ConnectionError("refused")):
            assert agent.generate_response("hi") is None

    def test_telemetry_failure_does_not_discard_successful_response(self):
        agent = Agent("T", "prompt", "ollama/qwen3")
        with (
            patch("litellm.completion", return_value=make_llm_response("draft")),
            patch("litellm.completion_cost", return_value=0.0),
            patch(
                "src.core.orchestrator.log_telemetry",
                side_effect=RuntimeError("telemetry db locked"),
            ),
        ):
            message = agent.generate_response("hi", raise_errors=True)
        assert message is not None
        assert message.content == "draft"
