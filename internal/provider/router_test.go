package provider

import (
	"errors"
	"testing"

	"github.com/howlcipher/ai_knowledge_library/internal/runtime"
)

// mockProvider is a minimal Provider implementation for exercising Router
// selection logic. Only Health is configurable per test; the remaining
// methods are stubs since Select never calls them.
type mockProvider struct {
	healthy   bool
	reason    string
	healthErr error
}

func (m *mockProvider) Probe() (Probe, error) { return Probe{}, nil }

func (m *mockProvider) Health() (Health, error) {
	if m.healthErr != nil {
		return Health{}, m.healthErr
	}
	return Health{Available: m.healthy, Reason: m.reason}, nil
}

func (m *mockProvider) Capabilities() []string { return nil }

func (m *mockProvider) Prepare(request *runtime.TaskRequest) (Invocation, error) {
	return Invocation{}, nil
}

func (m *mockProvider) Execute(invocation Invocation) (RawOutput, error) {
	return RawOutput{}, nil
}

func (m *mockProvider) Normalize(output RawOutput) ([]runtime.RunEvent, *runtime.RunResult, error) {
	return nil, nil, nil
}

func (m *mockProvider) ClassifyFailure(err error) runtime.FailureClass {
	return runtime.FailureUnknown
}

func (m *mockProvider) Redact(text string) string { return text }

func TestRouter_Select_SingleHealthyProvider(t *testing.T) {
	r := NewRouter()
	r.Register("codex", &mockProvider{healthy: true})

	p, decision, err := r.Select("implementation", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if p == nil {
		t.Fatalf("expected a provider, got nil")
	}
	if decision.Selected != "codex" {
		t.Errorf("expected selected 'codex', got %q", decision.Selected)
	}
	if len(decision.Excluded) != 0 {
		t.Errorf("expected no exclusions, got %v", decision.Excluded)
	}
}

func TestRouter_Select_PreferredUnhealthyFallsBack(t *testing.T) {
	r := NewRouter()
	r.Register("codex", &mockProvider{healthy: false, reason: "usage limit reached"})
	r.Register("claude", &mockProvider{healthy: true})

	p, decision, err := r.Select("implementation", []string{"codex", "claude"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if p == nil {
		t.Fatalf("expected a provider, got nil")
	}
	if decision.Selected != "claude" {
		t.Errorf("expected selected 'claude', got %q", decision.Selected)
	}
	reason, ok := decision.Excluded["codex"]
	if !ok {
		t.Fatalf("expected 'codex' to be excluded, got %v", decision.Excluded)
	}
	if reason != "unhealthy: usage limit reached" {
		t.Errorf("expected exclusion reason 'unhealthy: usage limit reached', got %q", reason)
	}
}

func TestRouter_Select_AllUnhealthyReturnsError(t *testing.T) {
	r := NewRouter()
	r.Register("codex", &mockProvider{healthy: false, reason: "usage limit"})
	r.Register("claude", &mockProvider{healthErr: errors.New("connection refused")})

	p, decision, err := r.Select("implementation", nil)
	if err == nil {
		t.Fatalf("expected error, got nil")
	}
	if p != nil {
		t.Fatalf("expected nil provider, got %v", p)
	}
	if decision.Selected != "" {
		t.Errorf("expected empty Selected, got %q", decision.Selected)
	}
	if len(decision.Excluded) != 2 {
		t.Errorf("expected 2 exclusions, got %v", decision.Excluded)
	}
}

func TestRouter_Select_EmptyPreferredUsesRegistrationOrder(t *testing.T) {
	r := NewRouter()
	r.Register("codex", &mockProvider{healthy: true})
	r.Register("claude", &mockProvider{healthy: true})

	_, decision, err := r.Select("implementation", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(decision.Candidates) != 2 || decision.Candidates[0] != "codex" || decision.Candidates[1] != "claude" {
		t.Fatalf("expected candidates [codex claude] in registration order, got %v", decision.Candidates)
	}
	if decision.Selected != "codex" {
		t.Errorf("expected selected 'codex' (first healthy in registration order), got %q", decision.Selected)
	}
}
