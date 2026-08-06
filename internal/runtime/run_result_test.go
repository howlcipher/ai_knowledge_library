package runtime

import (
	"path/filepath"
	"strings"
	"testing"
)

// TestLoadRunResult_Example ensures the example run result shipped under
// examples/runs/ is a legitimate, valid ai.run_result/v1 document per the
// current validation rules.
func TestLoadRunResult_Example(t *testing.T) {
	path := filepath.Join("..", "..", "examples", "runs", "run_result.json")
	res, err := LoadRunResult(path)
	if err != nil {
		t.Fatalf("expected %s to be a valid run result, got error: %v", path, err)
	}
	if res.Status != StatusSucceeded {
		t.Fatalf("expected status %q, got %q", StatusSucceeded, res.Status)
	}
	if res.Attempts != 1 {
		t.Fatalf("expected 1 attempt, got %d", res.Attempts)
	}
}

func TestParseRunResult_Invalid(t *testing.T) {
	tests := []struct {
		name        string
		json        string
		errContains string
	}{
		{
			name:        "wrong schema constant",
			json:        `{"schema":"wrong","run_id":"r1","status":"succeeded","provider":"codex","attempts":1,"summary":"done"}`,
			errContains: "invalid schema",
		},
		{
			name:        "missing run_id",
			json:        `{"schema":"ai.run_result/v1","status":"succeeded","provider":"codex","attempts":1,"summary":"done"}`,
			errContains: "run_id",
		},
		{
			name:        "missing provider",
			json:        `{"schema":"ai.run_result/v1","run_id":"r1","status":"succeeded","attempts":1,"summary":"done"}`,
			errContains: "provider",
		},
		{
			name:        "missing summary",
			json:        `{"schema":"ai.run_result/v1","run_id":"r1","status":"succeeded","provider":"codex","attempts":1}`,
			errContains: "summary",
		},
		{
			name:        "attempts less than one",
			json:        `{"schema":"ai.run_result/v1","run_id":"r1","status":"succeeded","provider":"codex","attempts":0,"summary":"done"}`,
			errContains: "attempts",
		},
		{
			name:        "invalid status enum",
			json:        `{"schema":"ai.run_result/v1","run_id":"r1","status":"exploded","provider":"codex","attempts":1,"summary":"done"}`,
			errContains: "unknown run status",
		},
		{
			name:        "failed without failure_class",
			json:        `{"schema":"ai.run_result/v1","run_id":"r1","status":"failed","provider":"codex","attempts":1,"summary":"done"}`,
			errContains: "failure_class",
		},
		{
			name:        "failed with invalid failure_class",
			json:        `{"schema":"ai.run_result/v1","run_id":"r1","status":"failed","failure_class":"not_a_class","provider":"codex","attempts":1,"summary":"done"}`,
			errContains: "failure_class",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := ParseRunResult(strings.NewReader(tc.json))
			if err == nil {
				t.Fatalf("expected error, got nil")
			}
			if !strings.Contains(err.Error(), tc.errContains) {
				t.Fatalf("expected error to contain %q, got %v", tc.errContains, err)
			}
		})
	}
}

func TestParseRunResult_FailedWithValidFailureClass(t *testing.T) {
	json := `{"schema":"ai.run_result/v1","run_id":"r1","status":"failed","failure_class":"network_transient","provider":"codex","attempts":2,"summary":"network blip"}`
	res, err := ParseRunResult(strings.NewReader(json))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !res.FailureClass.RetriableViaFallback() {
		t.Errorf("expected network_transient to be retriable via fallback")
	}
}
