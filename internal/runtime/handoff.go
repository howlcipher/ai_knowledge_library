package runtime

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
)

// handoffSchema is the exact $id value every Handoff document must
// declare, per schemas/handoff.schema.json.
const handoffSchema = "ai.handoff/v1"

// CommandRun records a single command executed during an interrupted run
// attempt and its outcome, matching the commands_run items in
// schemas/handoff.schema.json.
type CommandRun struct {
	Command string `json:"command"`
	Result  string `json:"result"`
}

// RecommendedNext captures the recommended provider and workflow to resume
// a handed-off run, matching schemas/handoff.schema.json. Both fields are
// required JSON keys but may legitimately be empty strings ("none
// recommended"), so Validate does not reject empty values here.
type RecommendedNext struct {
	Provider string `json:"provider"`
	Workflow string `json:"workflow"`
}

// Handoff is a structured summary of an interrupted or provider-switched
// run, matching schemas/handoff.schema.json.
type Handoff struct {
	Schema                      string          `json:"schema"`
	RunID                       string          `json:"run_id"`
	OriginalTask                string          `json:"original_task"`
	ProjectRoot                 string          `json:"project_root"`
	StartingCommit              string          `json:"starting_commit"`
	ContextReviewed             []string        `json:"context_reviewed"`
	WorkCompleted               string          `json:"work_completed"`
	FilesModified               []string        `json:"files_modified"`
	CommandsRun                 []CommandRun    `json:"commands_run"`
	FailureOrInterruptionReason string          `json:"failure_or_interruption_reason"`
	RemainingWork               []string        `json:"remaining_work"`
	SecurityConstraints         []string        `json:"security_constraints"`
	RecommendedNext             RecommendedNext `json:"recommended_next"`
}

// LoadHandoff reads and parses a Handoff document from the given path.
func LoadHandoff(path string) (*Handoff, error) {
	file, err := os.Open(path) // #nosec G304 -- caller-supplied path to a local run artifact, not untrusted network input
	if err != nil {
		return nil, fmt.Errorf("failed to open handoff: %w", err)
	}
	defer file.Close()
	return ParseHandoff(file)
}

// ParseHandoff decodes a Handoff document from r and validates it.
func ParseHandoff(r io.Reader) (*Handoff, error) {
	var h Handoff
	decoder := json.NewDecoder(r)
	if err := decoder.Decode(&h); err != nil {
		return nil, fmt.Errorf("failed to parse handoff: %w", err)
	}

	if err := h.Validate(); err != nil {
		return nil, err
	}

	return &h, nil
}

// Validate enforces the required-field rules from schemas/handoff.schema.json.
// recommended_next.provider, recommended_next.workflow, and each
// commands_run[].result are intentionally not checked for non-emptiness: the
// schema requires the keys to be present, not non-empty, since "no
// recommendation" and "no captured output" are legitimate values.
func (h *Handoff) Validate() error {
	if h.Schema != handoffSchema {
		return fmt.Errorf("invalid schema: expected %q, got %q", handoffSchema, h.Schema)
	}
	if h.RunID == "" {
		return fmt.Errorf("handoff is missing required field 'run_id'")
	}
	if h.OriginalTask == "" {
		return fmt.Errorf("handoff is missing required field 'original_task'")
	}
	if h.ProjectRoot == "" {
		return fmt.Errorf("handoff is missing required field 'project_root'")
	}
	if h.StartingCommit == "" {
		return fmt.Errorf("handoff is missing required field 'starting_commit'")
	}
	if h.FailureOrInterruptionReason == "" {
		return fmt.Errorf("handoff is missing required field 'failure_or_interruption_reason'")
	}

	for i, cmd := range h.CommandsRun {
		if cmd.Command == "" {
			return fmt.Errorf("handoff commands_run[%d] is missing required field 'command'", i)
		}
	}

	return nil
}
