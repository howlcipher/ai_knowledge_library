"""
test_control_plane_schemas.py

Validates control plane JSON schemas against Draft 2020-12 and checks example payloads.
"""

import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator, validate, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"

CONTROL_PLANE_SCHEMAS = [
    "task-spec.schema.json",
    "agent-registry.schema.json",
    "review-finding.schema.json",
    "verification-plan.schema.json",
    "evidence-entry.schema.json",
]


@pytest.mark.parametrize("schema_name", CONTROL_PLANE_SCHEMAS)
def test_control_plane_schema_is_valid_draft_2020_12(schema_name):
    schema_path = SCHEMA_DIR / schema_name
    assert schema_path.exists(), f"Missing schema file: {schema_path}"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_json = json.load(f)
    Draft202012Validator.check_schema(schema_json)


def test_task_spec_schema_validation():
    schema_path = SCHEMA_DIR / "task-spec.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    valid_payload = {
        "schema": "ai.task_spec/v1",
        "task_id": "TASK-100",
        "repository": "ai_knowledge_library",
        "objective": "Test objective",
        "acceptance_criteria": ["All tests pass"],
        "risk_level": "medium",
        "current_state": "discovered",
    }
    validate(instance=valid_payload, schema=schema)

    # Missing required field
    invalid_payload = {
        "schema": "ai.task_spec/v1",
        "task_id": "TASK-100",
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_payload, schema=schema)


def test_agent_registry_schema_validation():
    schema_path = SCHEMA_DIR / "agent-registry.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    valid_payload = {
        "schema": "ai.agent_registry/v1",
        "agents": [
            {
                "agent_id": "claude_code",
                "name": "Claude Code",
                "provider": "anthropic",
                "interface": "cli",
                "capabilities": ["code_generation"],
                "reasoning_tier": "tier_1",
                "cost_class": "subscription_included",
                "availability": "available",
            }
        ],
    }
    validate(instance=valid_payload, schema=schema)


def test_review_finding_schema_validation():
    schema_path = SCHEMA_DIR / "review-finding.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    valid_payload = {
        "schema": "ai.review_finding/v1",
        "id": "F001",
        "reviewer_role": "security-reviewer",
        "title": "Unsafe command execution",
        "severity": "high",
        "category": "security",
        "description": "shell=True used with untrusted input",
        "status": "open",
    }
    validate(instance=valid_payload, schema=schema)


def test_verification_plan_schema_validation():
    schema_path = SCHEMA_DIR / "verification-plan.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    valid_payload = {
        "schema": "ai.verification_plan/v1",
        "task_id": "TASK-100",
        "overall_status": "passed",
        "steps": [
            {
                "step_id": "step-01",
                "name": "Run tests",
                "command": "pytest",
                "category": "unit_test",
                "status": "verified",
                "required": True,
            }
        ],
    }
    validate(instance=valid_payload, schema=schema)


def test_evidence_entry_schema_validation():
    schema_path = SCHEMA_DIR / "evidence-entry.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    valid_payload = {
        "schema": "ai.evidence_entry/v1",
        "entry_id": "ev-123456",
        "task_id": "TASK-100",
        "agent_id": "claude_code",
        "action": "task_created",
        "timestamp": "2026-08-18T12:00:00Z",
    }
    validate(instance=valid_payload, schema=schema)
