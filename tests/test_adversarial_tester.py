"""Regression test for the adversarial tester's transport-error handling
(commit 10add63, improvements.md item 33): a provider that is merely
unreachable must never be scored as a successful safety rejection just
because the fallback error string happened to contain "blocked by safety"."""

import pytest
from unittest.mock import patch

from src.core.adversarial_tester import run_tests


@patch("src.core.adversarial_tester.load_config")
@patch("src.core.adversarial_tester.litellm.completion")
def test_transport_failure_is_skipped_not_scored_as_pass(mock_completion, mock_load_config, capsys):
    # No retries so the test doesn't sleep, and this proves the failure
    # isn't hidden behind retry exhaustion either.
    mock_load_config.return_value = {
        "payload_pipeline": {"transport_retries": 0, "transport_backoff": 0.0}
    }
    mock_completion.side_effect = RuntimeError("connection refused")

    with pytest.raises(SystemExit) as exc_info:
        run_tests(api_key="fake-key", model="fake/model")

    # All cases hit a transport error, so there is nothing to score.
    assert exc_info.value.code == 2
    assert mock_completion.called

    output = capsys.readouterr().out
    assert "[SKIP]" in output
    assert "[PASS]" not in output
    assert "0/0 passed" in output
