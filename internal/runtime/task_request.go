package runtime

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/howlcipher/howlplane/internal/capability"
)

// taskRequestSchema is the exact $id value every TaskRequest document must
// declare, per schemas/task-request.schema.json.
const taskRequestSchema = "ai.task_request/v1"

// TaskRequest represents a request to execute a task through the
// framework's workflow and provider runtime, matching
// schemas/task-request.schema.json.
type TaskRequest struct {
	Schema               string         `json:"schema"`
	Task                 string         `json:"task"`
	Mode                 string         `json:"mode"`
	ProjectRoot          string         `json:"project_root"`
	TaskType             string         `json:"task_type"`
	RequiredCapabilities []string       `json:"required_capabilities"`
	PreferredProviders   []string       `json:"preferred_providers"`
	Metadata             map[string]any `json:"metadata,omitempty"`
}

// LoadTaskRequest reads and parses a TaskRequest document from the given
// path.
func LoadTaskRequest(path string) (*TaskRequest, error) {
	file, err := os.Open(path) // #nosec G304 -- caller-supplied path to a local run artifact, not untrusted network input
	if err != nil {
		return nil, fmt.Errorf("failed to open task request: %w", err)
	}
	defer file.Close()
	return ParseTaskRequest(file)
}

// ParseTaskRequest decodes a TaskRequest document from r and validates it.
func ParseTaskRequest(r io.Reader) (*TaskRequest, error) {
	var t TaskRequest
	decoder := json.NewDecoder(r)
	if err := decoder.Decode(&t); err != nil {
		return nil, fmt.Errorf("failed to parse task request: %w", err)
	}

	if err := t.Validate(); err != nil {
		return nil, err
	}

	return &t, nil
}

// Validate enforces the required-field and enum rules from
// schemas/task-request.schema.json.
func (t *TaskRequest) Validate() error {
	if t.Schema != taskRequestSchema {
		return fmt.Errorf("invalid schema: expected %q, got %q", taskRequestSchema, t.Schema)
	}
	if t.Task == "" {
		return fmt.Errorf("task request is missing required field 'task'")
	}
	if t.Mode == "" {
		return fmt.Errorf("task request is missing required field 'mode'")
	}
	if t.ProjectRoot == "" {
		return fmt.Errorf("task request is missing required field 'project_root'")
	}
	if t.TaskType == "" {
		return fmt.Errorf("task request is missing required field 'task_type'")
	}

	for _, cap := range t.RequiredCapabilities {
		if !capability.IsKnown(cap) {
			return fmt.Errorf("unknown capability: %s", cap)
		}
	}

	return nil
}
