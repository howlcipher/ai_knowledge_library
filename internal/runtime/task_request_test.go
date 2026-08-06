package runtime

import (
	"path/filepath"
	"strings"
	"testing"
)

// TestLoadTaskRequest_Example ensures the example task request shipped
// under examples/runs/ is a legitimate, valid ai.task_request/v1 document
// per the current validation rules.
func TestLoadTaskRequest_Example(t *testing.T) {
	path := filepath.Join("..", "..", "examples", "runs", "task_request.json")
	tr, err := LoadTaskRequest(path)
	if err != nil {
		t.Fatalf("expected %s to be a valid task request, got error: %v", path, err)
	}
	if tr.Task == "" {
		t.Fatalf("expected %s to have a non-empty task", path)
	}
	if tr.Schema != taskRequestSchema {
		t.Fatalf("expected schema %q, got %q", taskRequestSchema, tr.Schema)
	}
}

func TestParseTaskRequest_Invalid(t *testing.T) {
	tests := []struct {
		name        string
		json        string
		errContains string
	}{
		{
			name:        "wrong schema constant",
			json:        `{"schema":"wrong","task":"t","mode":"edit","project_root":"/p","task_type":"implementation","required_capabilities":[],"preferred_providers":[]}`,
			errContains: "invalid schema",
		},
		{
			name:        "missing task",
			json:        `{"schema":"ai.task_request/v1","mode":"edit","project_root":"/p","task_type":"implementation","required_capabilities":[],"preferred_providers":[]}`,
			errContains: "task",
		},
		{
			name:        "missing mode",
			json:        `{"schema":"ai.task_request/v1","task":"t","project_root":"/p","task_type":"implementation","required_capabilities":[],"preferred_providers":[]}`,
			errContains: "mode",
		},
		{
			name:        "missing project_root",
			json:        `{"schema":"ai.task_request/v1","task":"t","mode":"edit","task_type":"implementation","required_capabilities":[],"preferred_providers":[]}`,
			errContains: "project_root",
		},
		{
			name:        "missing task_type",
			json:        `{"schema":"ai.task_request/v1","task":"t","mode":"edit","project_root":"/p","required_capabilities":[],"preferred_providers":[]}`,
			errContains: "task_type",
		},
		{
			name:        "unknown capability",
			json:        `{"schema":"ai.task_request/v1","task":"t","mode":"edit","project_root":"/p","task_type":"implementation","required_capabilities":["magic:allow"],"preferred_providers":[]}`,
			errContains: "unknown capability: magic:allow",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := ParseTaskRequest(strings.NewReader(tc.json))
			if err == nil {
				t.Fatalf("expected error, got nil")
			}
			if !strings.Contains(err.Error(), tc.errContains) {
				t.Fatalf("expected error to contain %q, got %v", tc.errContains, err)
			}
		})
	}
}

func TestParseTaskRequest_Valid(t *testing.T) {
	json := `{
		"schema": "ai.task_request/v1",
		"task": "Implement retry handling",
		"mode": "edit",
		"project_root": "/home/operator/projects/foo",
		"task_type": "implementation",
		"required_capabilities": ["filesystem:repository", "process:project_commands"],
		"preferred_providers": ["codex", "claude"]
	}`
	tr, err := ParseTaskRequest(strings.NewReader(json))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(tr.RequiredCapabilities) != 2 {
		t.Errorf("expected 2 required capabilities, got %d", len(tr.RequiredCapabilities))
	}
}
