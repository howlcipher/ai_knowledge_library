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

func TestParseManifest_ContextPaths(t *testing.T) {
	tests := []struct {
		name        string
		toml        string
		expectErr   bool
		errContains string
	}{
		{
			name: "absolute unix path in include",
			toml: `
schema_version = 1
name = "test"

[context]
include = ["/etc/passwd"]
`,
			expectErr:   true,
			errContains: "context.include path '/etc/passwd' must be relative to the repository root",
		},
		{
			name: "windows drive letter path in include",
			toml: `
schema_version = 1
name = "test"

[context]
include = ["C:\\secrets\\**"]
`,
			expectErr:   true,
			errContains: "context.include path 'C:\\secrets\\**' must be relative to the repository root",
		},
		{
			name: "path traversal via .. in exclude",
			toml: `
schema_version = 1
name = "test"

[context]
exclude = ["../../outside/**"]
`,
			expectErr:   true,
			errContains: "context.exclude path '../../outside/**' escapes repository root",
		},
		{
			name: "home directory shorthand in include",
			toml: `
schema_version = 1
name = "test"

[context]
include = ["~/secrets/**"]
`,
			expectErr:   true,
			errContains: "context.include path '~/secrets/**' must be relative to the repository root",
		},
		{
			name: "valid relative globs pass",
			toml: `
schema_version = 1
name = "test"

[context]
include = ["README.md", "docs/**/*.md", "pkg/**/*.go"]
exclude = [".env", "*.db", "applications/**", "logs/**"]
`,
			expectErr: false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := parseManifest(strings.NewReader(tc.toml))
			if tc.expectErr {
				if err == nil {
					t.Fatalf("expected error, got nil")
				}
				if !strings.Contains(err.Error(), tc.errContains) {
					t.Fatalf("expected error to contain %q, got %v", tc.errContains, err)
				}
			} else if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
		})
	}
}

func TestParseManifest_Commands(t *testing.T) {
	tests := []struct {
		name        string
		toml        string
		expectErr   bool
		errContains string
	}{
		{
			name: "command with disallowed metacharacter",
			toml: `
schema_version = 1
name = "test"

[commands]
test = ["sh", "-c", "go test ./... && rm -rf /"]
`,
			expectErr:   true,
			errContains: "disallowed shell metacharacter '&&'",
		},
		{
			name: "empty command array",
			toml: `
schema_version = 1
name = "test"

[commands]
test = []
`,
			expectErr:   true,
			errContains: "command 'test' has an empty argument array",
		},
		{
			name: "normal valid command array passes",
			toml: `
schema_version = 1
name = "test"

[commands]
test = ["go", "test", "./..."]
build = ["go", "build", "-o", "bin/service", "./cmd/service"]
`,
			expectErr: false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := parseManifest(strings.NewReader(tc.toml))
			if tc.expectErr {
				if err == nil {
					t.Fatalf("expected error, got nil")
				}
				if !strings.Contains(err.Error(), tc.errContains) {
					t.Fatalf("expected error to contain %q, got %v", tc.errContains, err)
				}
			} else if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
		})
	}
}
