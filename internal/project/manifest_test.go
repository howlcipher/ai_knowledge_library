package project

import (
	"strings"
	"testing"
)

func TestParseManifest_Valid(t *testing.T) {
	tomlData := `
schema_version = 1
name = "career-agent-core"
project_type = ["go", "automation", "browser"]
skills = ["career_automation", "secure_coding"]

[context]
include = ["README.md"]
exclude = ["*.db"]

[commands]
test = ["go", "test", "./..."]

[security]
capabilities = ["filesystem:repository", "network:public"]

[routing]
implementation = ["codex", "claude"]
`
	m, err := parseManifest(strings.NewReader(tomlData))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if m.SchemaVersion != 1 {
		t.Errorf("expected schema_version 1, got %d", m.SchemaVersion)
	}
	if m.Name != "career-agent-core" {
		t.Errorf("expected name career-agent-core, got %s", m.Name)
	}
	if len(m.Commands["test"]) != 3 {
		t.Errorf("expected 3 command arguments for 'test'")
	}
}

func TestParseManifest_InvalidVersion(t *testing.T) {
	tomlData := `
schema_version = 2
name = "test"
`
	_, err := parseManifest(strings.NewReader(tomlData))
	if err == nil {
		t.Fatalf("expected error for invalid schema version")
	}
}

func TestParseManifest_MissingName(t *testing.T) {
	tomlData := `
schema_version = 1
`
	_, err := parseManifest(strings.NewReader(tomlData))
	if err == nil {
		t.Fatalf("expected error for missing name")
	}
}

func TestParseManifest_UnknownCapability(t *testing.T) {
	tomlData := `
schema_version = 1
name = "test"

[security]
capabilities = ["filesystem:repository", "magic:allow"]
`
	_, err := parseManifest(strings.NewReader(tomlData))
	if err == nil || !strings.Contains(err.Error(), "unknown capability: magic:allow") {
		t.Fatalf("expected error for unknown capability, got %v", err)
	}
}

func TestParseManifest_ForwardCompatibleUnknownFields(t *testing.T) {
	tomlData := `
schema_version = 1
name = "test"
future_feature = "some_value"
`
	_, err := parseManifest(strings.NewReader(tomlData))
	if err != nil {
		t.Fatalf("unexpected error parsing unknown fields: %v", err)
	}
}
