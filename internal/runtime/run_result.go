package runtime

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
)

// runResultSchema is the exact $id value every RunResult document must
// declare, per schemas/run-result.schema.json.
const runResultSchema = "ai.run_result/v1"

// RunStatus is the final outcome of a run, per schemas/run-result.schema.json.
type RunStatus string

const (
	StatusSucceeded RunStatus = "succeeded"
	StatusFailed    RunStatus = "failed"
	StatusCancelled RunStatus = "cancelled"
	StatusHandedOff RunStatus = "handed_off"
)

var validRunStatuses = map[RunStatus]bool{
	StatusSucceeded: true,
	StatusFailed:    true,
	StatusCancelled: true,
	StatusHandedOff: true,
}

// RunResult is the final outcome record for a run, matching
// schemas/run-result.schema.json.
type RunResult struct {
	Schema       string         `json:"schema"`
	RunID        string         `json:"run_id"`
	Status       RunStatus      `json:"status"`
	FailureClass FailureClass   `json:"failure_class,omitempty"`
	Provider     string         `json:"provider"`
	Attempts     int            `json:"attempts"`
	Summary      string         `json:"summary"`
	Metadata     map[string]any `json:"metadata,omitempty"`
}

// LoadRunResult reads and parses a RunResult document from the given path.
func LoadRunResult(path string) (*RunResult, error) {
	file, err := os.Open(path) // #nosec G304 -- caller-supplied path to a local run artifact, not untrusted network input
	if err != nil {
		return nil, fmt.Errorf("failed to open run result: %w", err)
	}
	defer file.Close()
	return ParseRunResult(file)
}

// ParseRunResult decodes a RunResult document from r and validates it.
func ParseRunResult(r io.Reader) (*RunResult, error) {
	var res RunResult
	decoder := json.NewDecoder(r)
	if err := decoder.Decode(&res); err != nil {
		return nil, fmt.Errorf("failed to parse run result: %w", err)
	}

	if err := res.Validate(); err != nil {
		return nil, err
	}

	return &res, nil
}

// Validate enforces the required-field, enum, and conditional rules from
// schemas/run-result.schema.json, including the allOf/if/then rule that a
// failed run must carry a valid failure_class.
func (res *RunResult) Validate() error {
	if res.Schema != runResultSchema {
		return fmt.Errorf("invalid schema: expected %q, got %q", runResultSchema, res.Schema)
	}
	if res.RunID == "" {
		return fmt.Errorf("run result is missing required field 'run_id'")
	}
	if res.Provider == "" {
		return fmt.Errorf("run result is missing required field 'provider'")
	}
	if res.Summary == "" {
		return fmt.Errorf("run result is missing required field 'summary'")
	}
	if res.Attempts < 1 {
		return fmt.Errorf("run result 'attempts' must be >= 1, got %d", res.Attempts)
	}
	if !validRunStatuses[res.Status] {
		return fmt.Errorf("unknown run status: %s", res.Status)
	}

	// Section 8.3 / the schema's allOf/if/then: a failed run must be able to
	// say *why* in taxonomy terms, otherwise downstream routing can't decide
	// whether to fall back to another provider.
	if res.Status == StatusFailed {
		if res.FailureClass == "" || !res.FailureClass.IsValid() {
			return fmt.Errorf("run result with status 'failed' must have a valid 'failure_class'")
		}
	} else if res.FailureClass != "" && !res.FailureClass.IsValid() {
		return fmt.Errorf("unknown failure_class: %s", res.FailureClass)
	}

	return nil
}
