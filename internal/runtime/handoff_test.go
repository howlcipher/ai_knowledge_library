package runtime

import (
	"path/filepath"
	"strings"
	"testing"
)

// TestLoadHandoff_Example ensures the example handoff shipped under
// examples/runs/ is a legitimate, valid ai.handoff/v1 document per the
// current validation rules.
func TestLoadHandoff_Example(t *testing.T) {
	path := filepath.Join("..", "..", "examples", "runs", "handoff.json")
	h, err := LoadHandoff(path)
	if err != nil {
		t.Fatalf("expected %s to be a valid handoff, got error: %v", path, err)
	}
	if h.RunID == "" {
		t.Fatalf("expected %s to have a non-empty run_id", path)
	}
	if len(h.CommandsRun) == 0 {
		t.Fatalf("expected %s to have at least one command run", path)
	}
	if h.RecommendedNext.Provider != "claude" {
		t.Fatalf("expected recommended_next.provider %q, got %q", "claude", h.RecommendedNext.Provider)
	}
}

func TestParseHandoff_Invalid(t *testing.T) {
	valid := `{
		"schema": "ai.handoff/v1",
		"run_id": "r1",
		"original_task": "do the thing",
		"project_root": "/p",
		"starting_commit": "abc123",
		"context_reviewed": [],
		"work_completed": "",
		"files_modified": [],
		"commands_run": [{"command": "go test", "result": "ok"}],
		"failure_or_interruption_reason": "usage limit",
		"remaining_work": [],
		"security_constraints": [],
		"recommended_next": {"provider": "", "workflow": ""}
	}`

	// Sanity: the valid fixture above should parse cleanly.
	if _, err := ParseHandoff(strings.NewReader(valid)); err != nil {
		t.Fatalf("expected valid handoff to parse, got error: %v", err)
	}

	tests := []struct {
		name        string
		json        string
		errContains string
	}{
		{
			name: "wrong schema constant",
			json: `{"schema":"wrong","run_id":"r1","original_task":"t","project_root":"/p","starting_commit":"abc",
				"context_reviewed":[],"work_completed":"","files_modified":[],"commands_run":[],
				"failure_or_interruption_reason":"x","remaining_work":[],"security_constraints":[],
				"recommended_next":{"provider":"","workflow":""}}`,
			errContains: "invalid schema",
		},
		{
			name: "missing run_id",
			json: `{"schema":"ai.handoff/v1","original_task":"t","project_root":"/p","starting_commit":"abc",
				"context_reviewed":[],"work_completed":"","files_modified":[],"commands_run":[],
				"failure_or_interruption_reason":"x","remaining_work":[],"security_constraints":[],
				"recommended_next":{"provider":"","workflow":""}}`,
			errContains: "run_id",
		},
		{
			name: "missing original_task",
			json: `{"schema":"ai.handoff/v1","run_id":"r1","project_root":"/p","starting_commit":"abc",
				"context_reviewed":[],"work_completed":"","files_modified":[],"commands_run":[],
				"failure_or_interruption_reason":"x","remaining_work":[],"security_constraints":[],
				"recommended_next":{"provider":"","workflow":""}}`,
			errContains: "original_task",
		},
		{
			name: "missing project_root",
			json: `{"schema":"ai.handoff/v1","run_id":"r1","original_task":"t","starting_commit":"abc",
				"context_reviewed":[],"work_completed":"","files_modified":[],"commands_run":[],
				"failure_or_interruption_reason":"x","remaining_work":[],"security_constraints":[],
				"recommended_next":{"provider":"","workflow":""}}`,
			errContains: "project_root",
		},
		{
			name: "missing starting_commit",
			json: `{"schema":"ai.handoff/v1","run_id":"r1","original_task":"t","project_root":"/p",
				"context_reviewed":[],"work_completed":"","files_modified":[],"commands_run":[],
				"failure_or_interruption_reason":"x","remaining_work":[],"security_constraints":[],
				"recommended_next":{"provider":"","workflow":""}}`,
			errContains: "starting_commit",
		},
		{
			name: "missing failure_or_interruption_reason",
			json: `{"schema":"ai.handoff/v1","run_id":"r1","original_task":"t","project_root":"/p","starting_commit":"abc",
				"context_reviewed":[],"work_completed":"","files_modified":[],"commands_run":[],
				"remaining_work":[],"security_constraints":[],
				"recommended_next":{"provider":"","workflow":""}}`,
			errContains: "failure_or_interruption_reason",
		},
		{
			name: "command_run missing command",
			json: `{"schema":"ai.handoff/v1","run_id":"r1","original_task":"t","project_root":"/p","starting_commit":"abc",
				"context_reviewed":[],"work_completed":"","files_modified":[],
				"commands_run":[{"command":"","result":"ok"}],
				"failure_or_interruption_reason":"x","remaining_work":[],"security_constraints":[],
				"recommended_next":{"provider":"","workflow":""}}`,
			errContains: "commands_run[0]",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := ParseHandoff(strings.NewReader(tc.json))
			if err == nil {
				t.Fatalf("expected error, got nil")
			}
			if !strings.Contains(err.Error(), tc.errContains) {
				t.Fatalf("expected error to contain %q, got %v", tc.errContains, err)
			}
		})
	}
}

// TestParseHandoff_EmptyCommandResultIsValid ensures an empty commands_run[].result
// is accepted: schemas/handoff.schema.json requires the "result" key to be
// present, not non-empty ("no captured output" is a legitimate value), unlike
// "command", which does carry minLength: 1.
func TestParseHandoff_EmptyCommandResultIsValid(t *testing.T) {
	valid := `{
		"schema": "ai.handoff/v1",
		"run_id": "r1",
		"original_task": "do the thing",
		"project_root": "/p",
		"starting_commit": "abc123",
		"context_reviewed": [],
		"work_completed": "",
		"files_modified": [],
		"commands_run": [{"command": "go test", "result": ""}],
		"failure_or_interruption_reason": "usage limit",
		"remaining_work": [],
		"security_constraints": [],
		"recommended_next": {"provider": "", "workflow": ""}
	}`

	if _, err := ParseHandoff(strings.NewReader(valid)); err != nil {
		t.Fatalf("expected empty commands_run[].result to be valid, got error: %v", err)
	}
}
