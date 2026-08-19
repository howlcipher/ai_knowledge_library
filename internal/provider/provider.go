// Package provider defines the shared adapter contract every AI provider
// (Claude Code, Codex, Gemini, Ollama, ...) must implement, per blueprint
// section 8.2, plus a Router that selects among registered providers with
// an explainable decision trail (blueprint section 3.5).
//
// No adapter implementations exist yet in this repo; this interface and the
// Router are the extraction point future adapters plug into.
package provider

import "github.com/howlcipher/howlplane/internal/runtime"

// Probe reports whether a provider's executable is installed and, if so,
// its version.
type Probe struct {
	Installed bool
	Version   string
}

// Health reports a provider's current availability and, when unavailable,
// why.
type Health struct {
	Available bool
	Reason    string
}

// Invocation is a safe, fully-constructed provider command line ready to
// execute.
type Invocation struct {
	Command []string
	Env     map[string]string
}

// RawOutput is the unprocessed result of executing an Invocation, before a
// provider's Normalize step turns it into runtime events/results.
type RawOutput struct {
	Stdout   string
	Stderr   string
	ExitCode int
}

// Provider is the shared adapter contract every provider (Claude Code,
// Codex, Gemini, Ollama, ...) must implement, per blueprint section 8.2.
type Provider interface {
	Probe() (Probe, error)
	Health() (Health, error)
	Capabilities() []string
	Prepare(request *runtime.TaskRequest) (Invocation, error)
	Execute(invocation Invocation) (RawOutput, error)
	Normalize(output RawOutput) ([]runtime.RunEvent, *runtime.RunResult, error)
	ClassifyFailure(err error) runtime.FailureClass
	Redact(text string) string
}
