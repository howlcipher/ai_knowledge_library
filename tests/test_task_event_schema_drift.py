"""Guards the task/event/result/handoff schemas and example fixtures against drift.

`schemas/task-request.schema.json`, `schemas/run-event.schema.json`,
`schemas/run-result.schema.json`, `schemas/handoff.schema.json`, and
`schemas/failure-class.schema.json` are the machine-readable contract for
the Phase 2 run artifacts described in `documentation/AI_FRAMEWORK_BLUEPRINT.md`
section 11, and `examples/runs/*.json` are the files workflow authors copy
from. Nothing else in the repo validates the examples against these schemas,
so the two can silently diverge.

These tests parse every example fixture and validate it against its schema,
and additionally assert on inline dicts that the schemas themselves actually
enforce their rules (so a schema gutted down to `{}` would fail here rather
than passing vacuously).
"""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError, validate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
EXAMPLES_DIR = REPO_ROOT / "examples" / "runs"

TASK_REQUEST_SCHEMA_PATH = SCHEMA_DIR / "task-request.schema.json"
RUN_EVENT_SCHEMA_PATH = SCHEMA_DIR / "run-event.schema.json"
RUN_RESULT_SCHEMA_PATH = SCHEMA_DIR / "run-result.schema.json"
HANDOFF_SCHEMA_PATH = SCHEMA_DIR / "handoff.schema.json"
FAILURE_CLASS_SCHEMA_PATH = SCHEMA_DIR / "failure-class.schema.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def task_request_schema() -> dict:
    return _load_json(TASK_REQUEST_SCHEMA_PATH)


@pytest.fixture(scope="module")
def run_event_schema() -> dict:
    return _load_json(RUN_EVENT_SCHEMA_PATH)


@pytest.fixture(scope="module")
def run_result_schema() -> dict:
    return _load_json(RUN_RESULT_SCHEMA_PATH)


@pytest.fixture(scope="module")
def handoff_schema() -> dict:
    return _load_json(HANDOFF_SCHEMA_PATH)


@pytest.fixture(scope="module")
def failure_class_schema() -> dict:
    return _load_json(FAILURE_CLASS_SCHEMA_PATH)


def test_schemas_are_valid_draft_2020_12(
    task_request_schema,
    run_event_schema,
    run_result_schema,
    handoff_schema,
    failure_class_schema,
):
    for schema in (
        task_request_schema,
        run_event_schema,
        run_result_schema,
        handoff_schema,
        failure_class_schema,
    ):
        Draft202012Validator.check_schema(schema)


def test_all_four_example_fixtures_are_present():
    """The spec doc and the Go tests both assume these four artifacts stay covered."""
    paths = sorted(EXAMPLES_DIR.glob("*.json"))
    assert {p.name for p in paths} == {
        "task_request.json",
        "run_event.json",
        "run_result.json",
        "handoff.json",
    }


def test_example_task_request_matches_schema(task_request_schema):
    instance = _load_json(EXAMPLES_DIR / "task_request.json")
    validate(instance=instance, schema=task_request_schema)


def test_example_run_event_matches_schema(run_event_schema):
    instance = _load_json(EXAMPLES_DIR / "run_event.json")
    validate(instance=instance, schema=run_event_schema)


def test_example_run_result_matches_schema(run_result_schema):
    instance = _load_json(EXAMPLES_DIR / "run_result.json")
    validate(instance=instance, schema=run_result_schema)


def test_example_handoff_matches_schema(handoff_schema):
    instance = _load_json(EXAMPLES_DIR / "handoff.json")
    validate(instance=instance, schema=handoff_schema)


def test_example_task_request_capabilities_are_known(task_request_schema):
    capability_schema = _load_json(SCHEMA_DIR / "capability.schema.json")
    instance = _load_json(EXAMPLES_DIR / "task_request.json")
    for capability in instance["required_capabilities"]:
        validate(instance=capability, schema=capability_schema)


def test_failure_taxonomy_covers_every_documented_class(failure_class_schema):
    """Every failure class named in the blueprint's taxonomy must exist."""
    assert set(failure_class_schema["enum"]) == {
        "usage_limit",
        "authentication",
        "model_unavailable",
        "permission_or_approval",
        "network_transient",
        "provider_transient",
        "cancelled",
        "timeout",
        "task_failure",
        "invalid_output",
        "security_denied",
        "workspace_unsafe",
        "unknown",
    }


# --- Negative cases: prove the schemas enforce, not merely describe. ---


def _minimal_task_request() -> dict:
    return {
        "schema": "ai.task_request/v1",
        "task": "Do the thing",
        "mode": "edit",
        "project_root": "/repo",
        "task_type": "implementation",
        "required_capabilities": [],
        "preferred_providers": [],
    }


def test_minimal_task_request_is_valid(task_request_schema):
    validate(instance=_minimal_task_request(), schema=task_request_schema)


def test_task_request_missing_required_field_is_rejected(task_request_schema):
    for missing in (
        "schema",
        "task",
        "mode",
        "project_root",
        "task_type",
        "required_capabilities",
        "preferred_providers",
    ):
        instance = _minimal_task_request()
        del instance[missing]
        with pytest.raises(ValidationError):
            validate(instance=instance, schema=task_request_schema)


def test_task_request_wrong_schema_const_is_rejected(task_request_schema):
    instance = _minimal_task_request()
    instance["schema"] = "ai.task_request/v2"
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=task_request_schema)


def test_task_request_unknown_top_level_field_is_rejected(task_request_schema):
    """Unlike the project manifest, run artifacts are closed contracts per schema version."""
    instance = _minimal_task_request()
    instance["future_field_from_v2"] = "anything"
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=task_request_schema)


def _minimal_run_event() -> dict:
    return {
        "schema": "ai.run_event/v1",
        "run_id": "run_1",
        "attempt_id": "attempt_1",
        "timestamp": "2026-01-01T00:00:00Z",
        "source": "provider:codex",
        "type": "status",
        "payload": {},
    }


def test_minimal_run_event_is_valid(run_event_schema):
    validate(instance=_minimal_run_event(), schema=run_event_schema)


def test_run_event_invalid_type_is_rejected(run_event_schema):
    instance = _minimal_run_event()
    instance["type"] = "not_a_real_type"
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=run_event_schema)


def test_run_event_invalid_timestamp_is_rejected(run_event_schema):
    instance = _minimal_run_event()
    instance["timestamp"] = "not-a-timestamp"
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=run_event_schema)


def _minimal_run_result(status: str = "succeeded") -> dict:
    return {
        "schema": "ai.run_result/v1",
        "run_id": "run_1",
        "status": status,
        "provider": "codex",
        "attempts": 1,
        "summary": "Done.",
    }


def test_minimal_run_result_is_valid(run_result_schema):
    validate(instance=_minimal_run_result(), schema=run_result_schema)


def test_run_result_invalid_status_is_rejected(run_result_schema):
    instance = _minimal_run_result()
    instance["status"] = "in_progress"
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=run_result_schema)


def test_run_result_zero_attempts_is_rejected(run_result_schema):
    instance = _minimal_run_result()
    instance["attempts"] = 0
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=run_result_schema)


def test_run_result_failed_without_failure_class_is_rejected(run_result_schema):
    instance = _minimal_run_result(status="failed")
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=run_result_schema)


def test_run_result_failed_with_failure_class_is_valid(run_result_schema):
    instance = _minimal_run_result(status="failed")
    instance["failure_class"] = "provider_transient"
    validate(instance=instance, schema=run_result_schema)


def _minimal_handoff() -> dict:
    return {
        "schema": "ai.handoff/v1",
        "run_id": "run_1",
        "original_task": "Do the thing",
        "project_root": "/repo",
        "starting_commit": "abc1234",
        "context_reviewed": [],
        "work_completed": "",
        "files_modified": [],
        "commands_run": [],
        "failure_or_interruption_reason": "Usage limit reached",
        "remaining_work": [],
        "security_constraints": [],
        "recommended_next": {"provider": "", "workflow": ""},
    }


def test_minimal_handoff_is_valid(handoff_schema):
    validate(instance=_minimal_handoff(), schema=handoff_schema)


def test_handoff_missing_recommended_next_field_is_rejected(handoff_schema):
    instance = _minimal_handoff()
    del instance["recommended_next"]["workflow"]
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=handoff_schema)


def test_handoff_command_run_missing_result_is_rejected(handoff_schema):
    instance = _minimal_handoff()
    instance["commands_run"] = [{"command": "pytest"}]
    with pytest.raises(ValidationError):
        validate(instance=instance, schema=handoff_schema)


def test_invalid_failure_class_string_is_rejected(failure_class_schema):
    with pytest.raises(ValidationError):
        validate(instance="not_a_real_failure_class", schema=failure_class_schema)
