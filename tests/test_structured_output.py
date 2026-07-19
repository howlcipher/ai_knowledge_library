import json

from src.core.structured_output import (
    default_schema_path,
    payload_response_format,
    verification_response_format,
)


def test_response_format_shape():
    rf = payload_response_format()
    assert rf["type"] == "json_schema"
    assert rf["json_schema"]["name"] == "agent_task_payload"
    # Strict mode would reject the schema's optional fields; it must stay off.
    assert rf["json_schema"]["strict"] is False


def test_metadata_keys_stripped_but_constraints_kept():
    rf = payload_response_format()
    schema = rf["json_schema"]["schema"]
    assert "$schema" not in schema
    assert "$id" not in schema

    with open(default_schema_path(), "r", encoding="utf8") as f:
        original = json.load(f)
    original.pop("$schema")
    original.pop("$id")
    # Everything except the metadata keys travels to the provider unchanged.
    assert schema == original
    assert schema["properties"]["pipeline"]["allOf"]  # tier/pass conditionals


def test_source_schema_file_not_mutated():
    with open(default_schema_path(), "r", encoding="utf8") as f:
        before = f.read()
    payload_response_format()
    with open(default_schema_path(), "r", encoding="utf8") as f:
        assert f.read() == before


def test_custom_schema_path(tmp_path):
    path = tmp_path / "mini.schema.json"
    path.write_text(json.dumps({"$schema": "x", "$id": "y", "type": "object"}))
    rf = payload_response_format(str(path))
    assert rf["json_schema"]["schema"] == {"type": "object"}


def test_verification_response_format_shape():
    rf = verification_response_format()
    assert rf["type"] == "json_schema"
    assert rf["json_schema"]["name"] == "content_verification"
    schema = rf["json_schema"]["schema"]
    assert set(schema["properties"]) == {"verified", "confidence", "reason"}
    assert schema["required"] == ["verified", "confidence", "reason"]
    assert schema["additionalProperties"] is False


def test_verification_response_format_qualifies_for_strict_mode():
    # No optional fields and additionalProperties is False, so unlike the
    # payload schema this one meets OpenAI's strict-mode requirements.
    rf = verification_response_format()
    assert rf["json_schema"]["strict"] is True
