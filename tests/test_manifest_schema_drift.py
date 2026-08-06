"""Guards `.ai-project.toml` schemas and example manifests against drift.

`schemas/ai-project.schema.json` and `schemas/capability.schema.json` are the
machine-readable contract for the portable project manifest, and
`examples/manifests/*.toml` are the files project owners copy from. Nothing in
the Go build validates the examples against the JSON schemas, so the two can
silently diverge: an example gains a field the schema rejects, or a capability
string is renamed in one place only.

These tests parse every example manifest and validate it against both schemas,
and additionally assert on inline dicts that the schemas themselves actually
enforce their rules (so a schema gutted down to `{}` would fail here rather
than passing vacuously).
"""

import json
import tomllib
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError, validate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
MANIFEST_SCHEMA_PATH = SCHEMA_DIR / "ai-project.schema.json"
CAPABILITY_SCHEMA_PATH = SCHEMA_DIR / "capability.schema.json"
EXAMPLES_DIR = REPO_ROOT / "examples" / "manifests"

EXPECTED_EXAMPLE_COUNT = 4


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def example_manifest_paths() -> list:
    return sorted(EXAMPLES_DIR.glob("*.toml"))


@pytest.fixture(scope="module")
def manifest_schema() -> dict:
    return _load_json(MANIFEST_SCHEMA_PATH)


@pytest.fixture(scope="module")
def capability_schema() -> dict:
    return _load_json(CAPABILITY_SCHEMA_PATH)


def test_schemas_are_valid_draft_2020_12(manifest_schema, capability_schema):
    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(capability_schema)


def test_all_four_example_manifests_are_present():
    """The spec and the Go tests both assume these four stacks stay covered."""
    paths = example_manifest_paths()
    assert len(paths) == EXPECTED_EXAMPLE_COUNT, [p.name for p in paths]
    assert {p.name for p in paths} == {
        "generic-ai.toml",
        "go-service.toml",
        "python-tool.toml",
        "typescript-web.toml",
    }


@pytest.mark.parametrize(
    "manifest_path", example_manifest_paths(), ids=lambda p: p.name
)
def test_example_manifest_matches_project_schema(
    manifest_path, manifest_schema
):
    with open(manifest_path, "rb") as handle:
        manifest = tomllib.load(handle)

    validate(instance=manifest, schema=manifest_schema)


@pytest.mark.parametrize(
    "manifest_path", example_manifest_paths(), ids=lambda p: p.name
)
def test_example_manifest_capabilities_are_known(
    manifest_path, capability_schema
):
    with open(manifest_path, "rb") as handle:
        manifest = tomllib.load(handle)

    capabilities = manifest.get("security", {}).get("capabilities", [])
    assert capabilities, f"{manifest_path.name} declares no capabilities"

    for capability in capabilities:
        validate(instance=capability, schema=capability_schema)


def test_capability_enum_covers_every_documented_family(capability_schema):
    """Every family named in the blueprint's capability model must exist."""
    families = {value.split(":", 1)[0] for value in capability_schema["enum"]}
    assert families == {
        "filesystem",
        "network",
        "process",
        "browser",
        "git",
        "database",
        "secrets",
    }


# --- Negative cases: prove the schemas enforce, not merely describe. ---


def _minimal_valid_manifest() -> dict:
    return {"schema_version": 1, "name": "inline-fixture"}


def test_minimal_inline_manifest_is_valid(manifest_schema):
    validate(instance=_minimal_valid_manifest(), schema=manifest_schema)


def test_invalid_capability_string_is_rejected(capability_schema):
    with pytest.raises(ValidationError):
        validate(instance="filesystem:everything", schema=capability_schema)


def test_invalid_capability_in_manifest_is_rejected(capability_schema):
    manifest = _minimal_valid_manifest()
    manifest["security"] = {
        "capabilities": ["filesystem:repository", "network:all"]
    }

    with pytest.raises(ValidationError):
        for capability in manifest["security"]["capabilities"]:
            validate(instance=capability, schema=capability_schema)


@pytest.mark.parametrize("bad_version", [0, 2, "1", 1.5, [1], None])
def test_invalid_schema_version_is_rejected(manifest_schema, bad_version):
    """Note: JSON Schema treats 1.0 as an integer, so it is not tested here.
    Rejecting a TOML float literal is the decoder's job, not the schema's."""
    manifest = _minimal_valid_manifest()
    manifest["schema_version"] = bad_version

    with pytest.raises(ValidationError):
        validate(instance=manifest, schema=manifest_schema)


def test_missing_required_fields_are_rejected(manifest_schema):
    for missing in ("schema_version", "name"):
        manifest = _minimal_valid_manifest()
        del manifest[missing]
        with pytest.raises(ValidationError):
            validate(instance=manifest, schema=manifest_schema)


def test_shell_string_command_is_rejected(manifest_schema):
    """Commands are argv arrays; a bare shell string must not type-check."""
    manifest = _minimal_valid_manifest()
    manifest["commands"] = {"test": "go test ./..."}

    with pytest.raises(ValidationError):
        validate(instance=manifest, schema=manifest_schema)


def test_unknown_context_key_is_rejected(manifest_schema):
    """[context] is a closed table per the schema."""
    manifest = _minimal_valid_manifest()
    manifest["context"] = {"include": ["**/*.go"], "ignore": ["vendor/**"]}

    with pytest.raises(ValidationError):
        validate(instance=manifest, schema=manifest_schema)


def test_unknown_security_key_is_rejected(manifest_schema):
    """[security] is a closed table per the schema."""
    manifest = _minimal_valid_manifest()
    manifest["security"] = {"capabilities": [], "allow_everything": True}

    with pytest.raises(ValidationError):
        validate(instance=manifest, schema=manifest_schema)


def test_unknown_top_level_field_is_allowed(manifest_schema):
    """Forward compatibility: the parser must not reject unrecognized keys."""
    manifest = _minimal_valid_manifest()
    manifest["future_field_from_v2"] = {"anything": ["at", "all"]}

    validate(instance=manifest, schema=manifest_schema)
