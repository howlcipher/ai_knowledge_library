package runtime

import (
	"path/filepath"
	"strings"
	"testing"
)

// TestLoadRunEvent_Example ensures the example run event shipped under
// examples/runs/ is a legitimate, valid ai.run_event/v1 document per the
// current validation rules.
func TestLoadRunEvent_Example(t *testing.T) {
	path := filepath.Join("..", "..", "examples", "runs", "run_event.json")
	e, err := LoadRunEvent(path)
	if err != nil {
		t.Fatalf("expected %s to be a valid run event, got error: %v", path, err)
	}
	if e.RunID == "" {
		t.Fatalf("expected %s to have a non-empty run_id", path)
	}
	if e.Type != EventToolCall {
		t.Fatalf("expected type %q, got %q", EventToolCall, e.Type)
	}
}

func TestParseRunEvent_Invalid(t *testing.T) {
	base := map[string]string{
		"schema":     `"ai.run_event/v1"`,
		"run_id":     `"run_1"`,
		"attempt_id": `"attempt_1"`,
		"timestamp":  `"2026-02-14T18:32:05Z"`,
		"source":     `"provider:codex"`,
		"type":       `"tool_call"`,
		"payload":    `{"tool":"shell"}`,
	}
	build := func(overrides map[string]string, omit string) string {
		var sb strings.Builder
		sb.WriteString("{")
		first := true
		for k, v := range base {
			if k == omit {
				continue
			}
			if ov, ok := overrides[k]; ok {
				v = ov
			}
			if !first {
				sb.WriteString(",")
			}
			first = false
			sb.WriteString(`"` + k + `":` + v)
		}
		sb.WriteString("}")
		return sb.String()
	}

	tests := []struct {
		name        string
		json        string
		errContains string
	}{
		{
			name:        "wrong schema constant",
			json:        build(map[string]string{"schema": `"wrong"`}, ""),
			errContains: "invalid schema",
		},
		{
			name:        "missing run_id",
			json:        build(nil, "run_id"),
			errContains: "run_id",
		},
		{
			name:        "missing attempt_id",
			json:        build(nil, "attempt_id"),
			errContains: "attempt_id",
		},
		{
			name:        "missing source",
			json:        build(nil, "source"),
			errContains: "source",
		},
		{
			name:        "missing payload",
			json:        build(nil, "payload"),
			errContains: "payload",
		},
		{
			name:        "invalid event type",
			json:        build(map[string]string{"type": `"not_a_type"`}, ""),
			errContains: "unknown event type",
		},
		{
			name:        "invalid timestamp pattern",
			json:        build(map[string]string{"timestamp": `"not-a-timestamp"`}, ""),
			errContains: "does not match the required RFC 3339 pattern",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			_, err := ParseRunEvent(strings.NewReader(tc.json))
			if err == nil {
				t.Fatalf("expected error, got nil")
			}
			if !strings.Contains(err.Error(), tc.errContains) {
				t.Fatalf("expected error to contain %q, got %v", tc.errContains, err)
			}
		})
	}
}
