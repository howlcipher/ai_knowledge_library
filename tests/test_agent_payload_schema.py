import copy
import hashlib
import json
import os

import pytest
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "schemas",
    "agent_task_payload.schema.json",
)


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH, "r", encoding="utf8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def validator(schema):
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def sha256_of(body: str) -> str:
    return hashlib.sha256(body.encode("utf8")).hexdigest()


def make_pass1_payload():
    body = "# Draft\n\nInitial draft content produced by Tier 3."
    return {
        "schema_version": "1.0.0",
        "task_id": "1f0e6b0a-9c1d-4e7a-8b2f-3a4c5d6e7f80",
        "created_at": "2026-07-17T12:00:00Z",
        "updated_at": "2026-07-17T12:01:30Z",
        "pipeline": {
            "pass_number": 1,
            "pass_name": "draft_self_correct",
            "tier": 3,
            "agent_id": "gemini/gemini-1.5-flash",
            "status": "in_progress",
            "attempt": 1,
        },
        "routing": {
            "skills": [
                {"name": "cyber_security", "matched_by": "trigger", "trigger": "audit"},
                {"name": "technical_writing", "matched_by": "semantic", "score": 4.21},
            ]
        },
        "task": {
            "objective": "Produce a hardening runbook for the webhook server.",
            "domain": "cyber_security",
            "constraints": ["No external network calls"],
            "acceptance_criteria": ["Covers authentication", "Covers rate limiting"],
        },
        "content": {"format": "markdown", "body": body, "sha256": sha256_of(body)},
        "critique": {
            "verdict": "revise",
            "findings": [
                {
                    "id": "F001",
                    "severity": "low",
                    "category": "self_correction",
                    "summary": "Missing rate limiting section, added during self review.",
                    "disposition": "fixed",
                }
            ],
        },
        "lineage": {
            "revision": 0,
            "history": [
                {
                    "pass_number": 1,
                    "tier": 3,
                    "agent_id": "gemini/gemini-1.5-flash",
                    "completed_at": "2026-07-17T12:01:30Z",
                    "verdict": "revise",
                }
            ],
        },
    }


def make_pass2_payload():
    payload = make_pass1_payload()
    payload["pipeline"].update(
        {
            "pass_number": 2,
            "pass_name": "peer_review",
            "tier": 2,
            "agent_id": "anthropic/claude-sonnet-5",
        }
    )
    payload["critique"]["findings"].append(
        {
            "id": "F002",
            "severity": "high",
            "category": "security",
            "summary": "Webhook secret comparison is not constant time.",
            "evidence": "Section 'Authentication' uses ==",
            "suggested_fix": "Use hmac.compare_digest.",
        }
    )
    payload["critique"]["adversarial_tests"] = [
        {
            "name": "replayed_signature",
            "procedure": "Resend a captured valid webhook payload.",
            "expected": "Rejected via nonce or timestamp check.",
            "observed": "Accepted.",
            "passed": False,
        }
    ]
    payload["lineage"]["history"].append(
        {
            "pass_number": 2,
            "tier": 2,
            "agent_id": "anthropic/claude-sonnet-5",
            "completed_at": "2026-07-17T12:05:00Z",
            "verdict": "revise",
        }
    )
    return payload


def make_pass3_payload():
    payload = make_pass2_payload()
    body = "# Final Runbook\n\nHardened content with constant time comparison."
    payload["pipeline"].update(
        {
            "pass_number": 3,
            "pass_name": "final_synthesis",
            "tier": 1,
            "agent_id": "anthropic/claude-fable-5",
            "status": "approved",
        }
    )
    payload["content"] = {
        "format": "markdown",
        "body": body,
        "sha256": sha256_of(body),
    }
    for finding in payload["critique"]["findings"]:
        finding["disposition"] = "fixed"
    payload["critique"]["verdict"] = "approve"
    payload["lineage"]["history"].append(
        {
            "pass_number": 3,
            "tier": 1,
            "agent_id": "anthropic/claude-fable-5",
            "completed_at": "2026-07-17T12:09:00Z",
            "verdict": "approve",
        }
    )
    return payload


def make_failed_payload():
    payload = make_pass1_payload()
    payload["pipeline"]["status"] = "failed"
    payload["pipeline"]["attempt"] = 3
    payload["error"] = {
        "code": "SCHEMA_VALIDATION_FAILED",
        "message": "Model emitted fenced JSON after 3 attempts.",
        "failure_vector": "validation_gate.parse_model_output",
        "context": {"model": "gemini/gemini-1.5-flash"},
        "occurred_at": "2026-07-17T12:02:00Z",
    }
    return payload


def test_schema_is_valid_draft_2020_12(schema):
    Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize(
    "factory",
    [make_pass1_payload, make_pass2_payload, make_pass3_payload, make_failed_payload],
)
def test_valid_payloads_pass(validator, factory):
    errors = list(validator.iter_errors(factory()))
    assert errors == [], [e.message for e in errors]


def test_tier_pass_mismatch_rejected(validator):
    payload = make_pass1_payload()
    payload["pipeline"]["tier"] = 2
    assert not validator.is_valid(payload)


def test_pass_name_mismatch_rejected(validator):
    payload = make_pass1_payload()
    payload["pipeline"]["pass_name"] = "peer_review"
    assert not validator.is_valid(payload)


def test_additional_properties_rejected(validator):
    payload = make_pass1_payload()
    payload["commentary"] = "Here is the JSON you asked for!"
    assert not validator.is_valid(payload)


def test_bad_sha256_rejected(validator):
    payload = make_pass1_payload()
    payload["content"]["sha256"] = "not-a-hash"
    assert not validator.is_valid(payload)


def test_missing_required_rejected(validator):
    payload = make_pass1_payload()
    del payload["content"]
    assert not validator.is_valid(payload)


def test_bad_enum_rejected(validator):
    payload = make_pass1_payload()
    payload["critique"]["verdict"] = "LGTM"
    assert not validator.is_valid(payload)


def test_finding_id_format_enforced(validator):
    payload = make_pass1_payload()
    payload["critique"]["findings"][0]["id"] = "finding-1"
    assert not validator.is_valid(payload)


def test_null_optional_field_rejected(validator):
    payload = make_pass1_payload()
    payload["critique"]["findings"][0]["evidence"] = None
    assert not validator.is_valid(payload)


def test_gate_hash_check_example():
    payload = make_pass1_payload()
    tampered = copy.deepcopy(payload)
    tampered["content"]["body"] += " tampered"
    assert sha256_of(payload["content"]["body"]) == payload["content"]["sha256"]
    assert sha256_of(tampered["content"]["body"]) != tampered["content"]["sha256"]
