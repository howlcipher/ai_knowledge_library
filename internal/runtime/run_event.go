package runtime

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"regexp"
)

// runEventSchema is the exact $id value every RunEvent document must
// declare, per schemas/run-event.schema.json.
const runEventSchema = "ai.run_event/v1"

// EventType is the normalized event category for a RunEvent, per
// schemas/run-event.schema.json.
type EventType string

const (
	EventMessage    EventType = "message"
	EventToolCall   EventType = "tool_call"
	EventToolResult EventType = "tool_result"
	EventWarning    EventType = "warning"
	EventError      EventType = "error"
	EventStatus     EventType = "status"
	EventMetric     EventType = "metric"
)

var validEventTypes = map[EventType]bool{
	EventMessage:    true,
	EventToolCall:   true,
	EventToolResult: true,
	EventWarning:    true,
	EventError:      true,
	EventStatus:     true,
	EventMetric:     true,
}

// timestampPattern matches the RFC-3339-flavored timestamp format required
// by schemas/run-event.schema.json, compiled once at package init like
// windowsDriveLetterPattern in internal/project/manifest.go.
var timestampPattern = regexp.MustCompile(`^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$`)

// RunEvent is a single normalized event emitted by a provider or workflow
// stage during a run, matching schemas/run-event.schema.json.
type RunEvent struct {
	Schema    string         `json:"schema"`
	RunID     string         `json:"run_id"`
	AttemptID string         `json:"attempt_id"`
	Timestamp string         `json:"timestamp"`
	Source    string         `json:"source"`
	Type      EventType      `json:"type"`
	Payload   map[string]any `json:"payload"`
}

// LoadRunEvent reads and parses a RunEvent document from the given path.
func LoadRunEvent(path string) (*RunEvent, error) {
	file, err := os.Open(path) // #nosec G304 -- caller-supplied path to a local run artifact, not untrusted network input
	if err != nil {
		return nil, fmt.Errorf("failed to open run event: %w", err)
	}
	defer file.Close()
	return ParseRunEvent(file)
}

// ParseRunEvent decodes a RunEvent document from r and validates it.
func ParseRunEvent(r io.Reader) (*RunEvent, error) {
	var e RunEvent
	decoder := json.NewDecoder(r)
	if err := decoder.Decode(&e); err != nil {
		return nil, fmt.Errorf("failed to parse run event: %w", err)
	}

	if err := e.Validate(); err != nil {
		return nil, err
	}

	return &e, nil
}

// Validate enforces the required-field, enum, and timestamp-pattern rules
// from schemas/run-event.schema.json.
func (e *RunEvent) Validate() error {
	if e.Schema != runEventSchema {
		return fmt.Errorf("invalid schema: expected %q, got %q", runEventSchema, e.Schema)
	}
	if e.RunID == "" {
		return fmt.Errorf("run event is missing required field 'run_id'")
	}
	if e.AttemptID == "" {
		return fmt.Errorf("run event is missing required field 'attempt_id'")
	}
	if e.Source == "" {
		return fmt.Errorf("run event is missing required field 'source'")
	}
	if e.Timestamp == "" {
		return fmt.Errorf("run event is missing required field 'timestamp'")
	}
	if !timestampPattern.MatchString(e.Timestamp) {
		return fmt.Errorf("run event timestamp %q does not match the required RFC 3339 pattern", e.Timestamp)
	}
	if !validEventTypes[e.Type] {
		return fmt.Errorf("unknown event type: %s", e.Type)
	}
	if e.Payload == nil {
		return fmt.Errorf("run event is missing required field 'payload'")
	}

	return nil
}
