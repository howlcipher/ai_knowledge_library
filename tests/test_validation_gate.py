import copy
import json
from unittest.mock import MagicMock, patch

import pytest

from src.core.validation_gate import (
    ValidationGate,
    build_initial_payload,
    sha256_of,
)

TASK_ID = "11111111-1111-4111-8111-111111111111"
NOW = "2026-07-17T12:00:00Z"


@pytest.fixture(autouse=True)
def deterministic_ids(monkeypatch):
    monkeypatch.setattr("src.core.validation_gate.uuid4", lambda: TASK_ID)
    monkeypatch.setattr("src.core.validation_gate.utc_now", lambda: NOW)


@pytest.fixture
def gate():
    return ValidationGate(max_attempts=3)


def make_initial(query="Write a runbook."):
    return build_initial_payload(query, "general", [])


def make_pass1(initial):
    payload = copy.deepcopy(initial)
    body = "# Draft\n\nTier 3 draft."
    payload["content"] = {"format": "markdown", "body": body, "sha256": sha256_of(body)}
    payload["pipeline"]["agent_id"] = "tier3"
    payload["critique"] = {"verdict": "revise", "findings": []}
    payload["lineage"]["history"].append(
        {"pass_number": 1, "tier": 3, "agent_id": "tier3", "completed_at": NOW}
    )
    payload["updated_at"] = NOW
    return payload


def make_pass2(pass1):
    payload = copy.deepcopy(pass1)
    payload["pipeline"].update(
        {"pass_number": 2, "pass_name": "peer_review", "tier": 2, "agent_id": "tier2"}
    )
    payload["critique"]["findings"].append(
        {
            "id": "F001",
            "severity": "medium",
            "category": "correctness",
            "summary": "Draft lacks a rollback section.",
            "suggested_fix": "Add a rollback section.",
        }
    )
    payload["critique"]["adversarial_tests"] = [
        {
            "name": "empty_input",
            "procedure": "Apply runbook to an empty host.",
            "expected": "Graceful failure.",
            "observed": "Undefined.",
            "passed": False,
        }
    ]
    payload["lineage"]["history"].append(
        {
            "pass_number": 2,
            "tier": 2,
            "agent_id": "tier2",
            "completed_at": NOW,
            "verdict": "revise",
        }
    )
    return payload


def make_pass3(pass2):
    payload = copy.deepcopy(pass2)
    body = "# Final\n\nHardened asset with rollback section."
    payload["pipeline"].update(
        {
            "pass_number": 3,
            "pass_name": "final_synthesis",
            "tier": 1,
            "agent_id": "tier1",
            "status": "approved",
        }
    )
    payload["content"] = {"format": "markdown", "body": body, "sha256": sha256_of(body)}
    for finding in payload["critique"]["findings"]:
        finding["disposition"] = "fixed"
    payload["critique"]["verdict"] = "approve"
    payload["lineage"]["history"].append(
        {
            "pass_number": 3,
            "tier": 1,
            "agent_id": "tier1",
            "completed_at": NOW,
            "verdict": "approve",
        }
    )
    return payload


def test_parse_rejects_fenced_output(gate):
    result = gate.check("```json\n{}\n```")
    assert not result.ok
    assert result.stage == "parse"


def test_parse_rejects_prose_prefix(gate):
    result = gate.check('Here is the JSON: {"a": 1}')
    assert not result.ok
    assert result.stage == "parse"


def test_valid_pass1_accepted(gate):
    initial = make_initial()
    result = gate.check(json.dumps(make_pass1(initial)), prev=initial, expected_pass=1)
    assert result.ok, result.errors


def test_wrong_pass_number_rejected(gate):
    initial = make_initial()
    result = gate.check(json.dumps(make_pass1(initial)), prev=initial, expected_pass=2)
    assert not result.ok
    assert result.stage == "pass_check"


def test_pass2_hash_mismatch_rejected(gate):
    initial = make_initial()
    pass1 = make_pass1(initial)
    # Start with a correct pass2 payload
    payload = make_pass2(pass1)
    # Tamper body without updating sha256 (which will be correct from make_pass2)
    payload["content"]["body"] += " tampered"
    # Keep the original sha256 (so mismatch)
    result = gate.check(json.dumps(payload), prev=pass1, expected_pass=2)
    assert not result.ok
    assert result.stage == "hash"


def test_pass1_hash_stamped_not_verified(gate):
    initial = make_initial()
    payload = make_pass1(initial)
    body = payload["content"]["body"]
    payload["content"]["sha256"] = "0" * 64
    result = gate.check(json.dumps(payload), prev=initial, expected_pass=1)
    assert result.ok, result.errors
    assert result.payload["content"]["sha256"] == sha256_of(body)


def test_pass3_hash_stamped_not_verified(gate):
    pass1 = make_pass1(make_initial())
    pass2 = make_pass2(pass1)
    payload = make_pass3(pass2)
    body = payload["content"]["body"]
    payload["content"]["sha256"] = "0" * 64
    result = gate.check(json.dumps(payload), prev=pass2, expected_pass=3)
    assert result.ok, result.errors
    assert result.payload["content"]["sha256"] == sha256_of(body)


def test_task_mutation_rejected(gate):
    initial = make_initial()
    payload = make_pass1(initial)
    payload["task"]["objective"] = "Something else entirely."
    result = gate.check(json.dumps(payload), prev=initial, expected_pass=1)
    assert not result.ok
    assert result.stage == "mutation"


def test_pass2_content_mutation_rejected(gate):
    pass1 = make_pass1(make_initial())
    payload = make_pass2(pass1)
    body = "Rewritten by the reviewer."
    payload["content"] = {"format": "markdown", "body": body, "sha256": sha256_of(body)}
    result = gate.check(json.dumps(payload), prev=pass1, expected_pass=2)
    assert not result.ok
    assert any("content" in e for e in result.errors)


def test_pass2_finding_rewrite_rejected(gate):
    pass1 = make_pass1(make_initial())
    pass1["critique"]["findings"].append(
        {
            "id": "F001",
            "severity": "low",
            "category": "self_correction",
            "summary": "Fixed typo.",
            "disposition": "fixed",
        }
    )
    payload = make_pass2(pass1)
    payload["critique"]["findings"][0]["summary"] = "Rewritten history."
    result = gate.check(json.dumps(payload), prev=pass1, expected_pass=2)
    assert not result.ok
    assert any("append only" in e for e in result.errors)


def test_history_must_grow_by_one(gate):
    initial = make_initial()
    payload = make_pass1(initial)
    payload["lineage"]["history"] = []
    result = gate.check(json.dumps(payload), prev=initial, expected_pass=1)
    assert not result.ok
    assert any("exactly one" in e for e in result.errors)


def test_run_retries_with_feedback_then_succeeds(gate):
    initial = make_initial()
    good = json.dumps(make_pass1(initial))
    feedbacks = []

    def call_fn(feedback):
        feedbacks.append(feedback)
        return "```json\n{}\n```" if feedback is None else good

    result = gate.run(call_fn, prev=initial, expected_pass=1)
    assert result.ok
    assert result.attempts == 2
    assert result.payload["pipeline"]["attempt"] == 2
    assert feedbacks[0] is None
    assert feedbacks[1].startswith("VALIDATION ERROR:")


def test_run_exhaustion_builds_failed_payload(gate):
    initial = make_initial()
    result = gate.run(lambda fb: "not json at all", prev=initial, expected_pass=1)
    assert not result.ok
    assert result.attempts == 3
    failed = result.payload
    assert failed["pipeline"]["status"] == "failed"
    assert failed["error"]["code"] == "SCHEMA_VALIDATION_FAILED"
    assert failed["error"]["failure_vector"] == "validation_gate.parse"
    assert gate.schema_errors(failed) == []


def make_llm_response(content):
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=content, tool_calls=None))]
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 20
    response.usage.total_tokens = 30
    return response


def test_orchestrator_payload_loop_end_to_end(tmp_path, monkeypatch):
    cfg = {
        "llm_model": "gemini/gemini-1.5-pro",
        "active_mcps": [],
        "mcp_servers": {},
        "skill_router": {"enabled": False},
        "payload_pipeline": {
            "enabled": True,
            "max_attempts": 3,
            "preflight": False,
            "artifact_dir": str(tmp_path / "payloads"),
        },
    }
    monkeypatch.setattr("src.core.orchestrator.load_config", lambda: cfg)

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    query = "Write a runbook."
    initial = make_initial(query)
    pass1 = make_pass1(initial)
    pass2 = make_pass2(pass1)
    pass3 = make_pass3(pass2)
    responses = [make_llm_response(json.dumps(p)) for p in (pass1, pass2, pass3)]

    with (
        patch("litellm.completion", side_effect=responses),
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
    ):
        final = orchestrator.run_loop(query)

    assert final["pipeline"]["status"] == "approved"
    assert final["pipeline"]["pass_number"] == 3
    assert final["content"]["body"].startswith("# Final")

    artifact_dir = tmp_path / "payloads" / TASK_ID
    assert sorted(p.name for p in artifact_dir.iterdir()) == [
        "pass_1.json",
        "pass_2.json",
        "pass_3.json",
    ]


def test_orchestrator_payload_loop_halts_on_invalid_output(tmp_path, monkeypatch):
    cfg = {
        "llm_model": "gemini/gemini-1.5-pro",
        "active_mcps": [],
        "mcp_servers": {},
        "skill_router": {"enabled": False},
        "payload_pipeline": {
            "enabled": True,
            "max_attempts": 2,
            "preflight": False,
            "artifact_dir": str(tmp_path / "payloads"),
        },
    }
    monkeypatch.setattr("src.core.orchestrator.load_config", lambda: cfg)

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    bad = make_llm_response("Here is the JSON you asked for: {}")
    with (
        patch("litellm.completion", side_effect=[bad, bad]),
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
    ):
        final = orchestrator.run_loop("Write a runbook.")

    assert final["pipeline"]["status"] == "failed"
    assert final["error"]["code"] == "SCHEMA_VALIDATION_FAILED"


def test_orchestrator_uses_per_tier_models(tmp_path, monkeypatch):
    cfg = {
        "llm_model": "gemini/gemini-1.5-pro",
        "active_mcps": [],
        "mcp_servers": {},
        "skill_router": {"enabled": False},
        "payload_pipeline": {
            "enabled": True,
            "max_attempts": 3,
            "preflight": False,
            "artifact_dir": str(tmp_path / "payloads"),
            "tier_models": {
                "tier_1": "anthropic/claude-fable-5",
                "tier_2": "anthropic/claude-sonnet-5",
                "tier_3": "",
            },
        },
    }
    monkeypatch.setattr("src.core.orchestrator.load_config", lambda: cfg)

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    query = "Write a runbook."
    initial = make_initial(query)
    pass1 = make_pass1(initial)
    pass2 = make_pass2(pass1)
    pass3 = make_pass3(pass2)
    responses = [make_llm_response(json.dumps(p)) for p in (pass1, pass2, pass3)]

    with (
        patch("litellm.completion", side_effect=responses) as mock_completion,
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
    ):
        final = orchestrator.run_loop(query)

    assert final["pipeline"]["status"] == "approved"
    models_used = [c.kwargs["model"] for c in mock_completion.call_args_list]
    # Pass order is tier 3 draft, tier 2 review, tier 1 synthesis; empty
    # tier_3 override falls back to the top level llm_model.
    assert models_used == [
        "gemini/gemini-1.5-pro",
        "anthropic/claude-sonnet-5",
        "anthropic/claude-fable-5",
    ]


def test_build_failed_payload_custom_code_vector_and_context(gate):
    prev = make_initial()
    failed = gate.build_failed_payload(
        prev,
        ["Provider unavailable after 3 attempts: ConnectionError: refused"],
        stage="transport",
        code="UPSTREAM_UNAVAILABLE",
        failure_vector="llm_transport.completion",
        context={"model": "ollama/qwen3", "attempt_errors": ["refused"]},
    )
    assert failed["pipeline"]["status"] == "failed"
    assert failed["error"]["code"] == "UPSTREAM_UNAVAILABLE"
    assert failed["error"]["failure_vector"] == "llm_transport.completion"
    assert failed["error"]["context"]["model"] == "ollama/qwen3"
    assert failed["error"]["context"]["attempt_errors"] == ["refused"]
    # Defaults are unchanged for gate exhaustion callers.
    default = gate.build_failed_payload(prev, ["bad json"], stage="parse")
    assert default["error"]["code"] == "SCHEMA_VALIDATION_FAILED"
    assert default["error"]["failure_vector"] == "validation_gate.parse"
    assert default["error"]["context"] == {"max_attempts": 3}


def test_orchestrator_dead_provider_reports_upstream_unavailable(
    tmp_path, monkeypatch
):
    """A provider that stays down is retried at the transport layer only and
    aborts with UPSTREAM_UNAVAILABLE; no validation attempt is consumed."""
    cfg = {
        "llm_model": "gemini/gemini-1.5-pro",
        "active_mcps": [],
        "mcp_servers": {},
        "skill_router": {"enabled": False},
        "payload_pipeline": {
            "enabled": True,
            "max_attempts": 3,
            "preflight": False,
            "artifact_dir": str(tmp_path / "payloads"),
            "transport_retries": 1,
            "transport_backoff": 0.0,
        },
    }
    monkeypatch.setattr("src.core.orchestrator.load_config", lambda: cfg)

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    with (
        patch(
            "litellm.completion",
            side_effect=ConnectionError("connection refused"),
        ) as mock_completion,
        patch("src.core.transport_retry.time.sleep"),
    ):
        final = orchestrator.run_loop("Write a runbook.")

    assert final["pipeline"]["status"] == "failed"
    assert final["error"]["code"] == "UPSTREAM_UNAVAILABLE"
    assert final["error"]["failure_vector"] == "llm_transport.completion"
    assert final["error"]["context"]["model"] == "gemini/gemini-1.5-pro"
    assert final["error"]["context"]["transport_attempts"] == 2
    assert all(
        "connection refused" in e
        for e in final["error"]["context"]["attempt_errors"]
    )
    # Transport retries only: 1 + 1 retry. With the old behavior the gate
    # would have burned all 3 validation attempts (3 calls) on parse errors.
    assert mock_completion.call_count == 2
    # The failed payload is persisted for the post mortem.
    artifact_dir = tmp_path / "payloads" / TASK_ID
    assert [p.name for p in artifact_dir.iterdir()] == ["pass_1.json"]


def test_orchestrator_transient_provider_failure_recovers(tmp_path, monkeypatch):
    """One connection error is retried with backoff and the run completes
    without the gate ever seeing an empty response."""
    cfg = {
        "llm_model": "gemini/gemini-1.5-pro",
        "active_mcps": [],
        "mcp_servers": {},
        "skill_router": {"enabled": False},
        "payload_pipeline": {
            "enabled": True,
            "max_attempts": 3,
            "preflight": False,
            "artifact_dir": str(tmp_path / "payloads"),
            "transport_retries": 2,
            "transport_backoff": 0.0,
        },
    }
    monkeypatch.setattr("src.core.orchestrator.load_config", lambda: cfg)

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    query = "Write a runbook."
    initial = make_initial(query)
    pass1 = make_pass1(initial)
    pass2 = make_pass2(pass1)
    pass3 = make_pass3(pass2)
    responses = [
        ConnectionError("blip"),
        make_llm_response(json.dumps(pass1)),
        make_llm_response(json.dumps(pass2)),
        make_llm_response(json.dumps(pass3)),
    ]

    with (
        patch("litellm.completion", side_effect=responses) as mock_completion,
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
        patch("src.core.transport_retry.time.sleep"),
    ):
        final = orchestrator.run_loop(query)

    assert final["pipeline"]["status"] == "approved"
    assert final["pipeline"]["pass_number"] == 3
    # The retried call is a transport retry, not a validation attempt.
    assert final["pipeline"]["attempt"] == 1
    assert mock_completion.call_count == 4


def test_orchestrator_uses_per_tier_timeouts(tmp_path, monkeypatch):
    cfg = {
        "llm_model": "gemini/gemini-1.5-pro",
        "active_mcps": [],
        "mcp_servers": {},
        "skill_router": {"enabled": False},
        "payload_pipeline": {
            "enabled": True,
            "max_attempts": 3,
            "preflight": False,
            "artifact_dir": str(tmp_path / "payloads"),
            "timeout": 900.0,
            "tier_timeouts": {"tier_1": 0, "tier_2": 0, "tier_3": 1800.0},
        },
    }
    monkeypatch.setattr("src.core.orchestrator.load_config", lambda: cfg)

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    query = "Write a runbook."
    initial = make_initial(query)
    pass1 = make_pass1(initial)
    pass2 = make_pass2(pass1)
    pass3 = make_pass3(pass2)
    responses = [make_llm_response(json.dumps(p)) for p in (pass1, pass2, pass3)]

    with (
        patch("litellm.completion", side_effect=responses) as mock_completion,
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
    ):
        final = orchestrator.run_loop(query)

    assert final["pipeline"]["status"] == "approved"
    timeouts_used = [c.kwargs["timeout"] for c in mock_completion.call_args_list]
    # Pass order is tier 3 draft, tier 2 review, tier 1 synthesis; zero
    # overrides fall back to the pipeline level timeout.
    assert timeouts_used == [1800.0, 900.0, 900.0]


def _pipeline_cfg(tmp_path, **payload_overrides):
    payload = {
        "enabled": True,
        "max_attempts": 3,
        "preflight": False,
        "artifact_dir": str(tmp_path / "payloads"),
    }
    payload.update(payload_overrides)
    return {
        "llm_model": "gemini/gemini-1.5-pro",
        "active_mcps": [],
        "mcp_servers": {},
        "skill_router": {"enabled": False},
        "payload_pipeline": payload,
    }


def test_orchestrator_passes_schema_response_format(tmp_path, monkeypatch):
    # structured_outputs defaults on: every tier call carries the payload schema.
    monkeypatch.setattr(
        "src.core.orchestrator.load_config", lambda: _pipeline_cfg(tmp_path)
    )

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    query = "Write a runbook."
    initial = make_initial(query)
    pass1 = make_pass1(initial)
    pass2 = make_pass2(pass1)
    pass3 = make_pass3(pass2)
    responses = [make_llm_response(json.dumps(p)) for p in (pass1, pass2, pass3)]

    with (
        patch("litellm.completion", side_effect=responses) as mock_completion,
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
    ):
        final = orchestrator.run_loop(query)

    assert final["pipeline"]["status"] == "approved"
    for call in mock_completion.call_args_list:
        rf = call.kwargs["response_format"]
        assert rf["type"] == "json_schema"
        assert rf["json_schema"]["name"] == "agent_task_payload"
        assert "$schema" not in rf["json_schema"]["schema"]
        assert "pipeline" in rf["json_schema"]["schema"]["properties"]


def test_orchestrator_structured_outputs_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.core.orchestrator.load_config",
        lambda: _pipeline_cfg(tmp_path, structured_outputs=False),
    )

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    query = "Write a runbook."
    initial = make_initial(query)
    pass1 = make_pass1(initial)
    pass2 = make_pass2(pass1)
    pass3 = make_pass3(pass2)
    responses = [make_llm_response(json.dumps(p)) for p in (pass1, pass2, pass3)]

    with (
        patch("litellm.completion", side_effect=responses) as mock_completion,
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
    ):
        final = orchestrator.run_loop(query)

    assert final["pipeline"]["status"] == "approved"
    for call in mock_completion.call_args_list:
        assert "response_format" not in call.kwargs


def test_orchestrator_survives_response_format_build_failure(tmp_path, monkeypatch):
    # A broken schema file must degrade to prompt-only discipline, not kill the run.
    monkeypatch.setattr(
        "src.core.orchestrator.load_config", lambda: _pipeline_cfg(tmp_path)
    )
    monkeypatch.setattr(
        "src.core.structured_output.payload_response_format",
        MagicMock(side_effect=OSError("schema unreadable")),
    )

    from src.core.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    orchestrator.skill_router = None

    query = "Write a runbook."
    initial = make_initial(query)
    pass1 = make_pass1(initial)
    pass2 = make_pass2(pass1)
    pass3 = make_pass3(pass2)
    responses = [make_llm_response(json.dumps(p)) for p in (pass1, pass2, pass3)]

    with (
        patch("litellm.completion", side_effect=responses) as mock_completion,
        patch("litellm.completion_cost", return_value=0.0),
        patch("src.core.orchestrator.log_telemetry"),
    ):
        final = orchestrator.run_loop(query)

    assert final["pipeline"]["status"] == "approved"
    for call in mock_completion.call_args_list:
        assert "response_format" not in call.kwargs
