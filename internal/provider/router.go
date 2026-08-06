package provider

import "fmt"

// RouteDecision documents why a particular provider was (or was not)
// selected for a task, per blueprint section 3.5: "Every route decision
// should state the task classification, candidate providers, health
// exclusions, historical signals, user overrides, and final selection."
type RouteDecision struct {
	TaskType   string
	Candidates []string          // providers considered, in preference order
	Excluded   map[string]string // provider name -> exclusion reason (e.g. "unhealthy: <Health.Reason>")
	Selected   string            // empty if none selected
}

// Router holds a registry of named providers and selects among them.
type Router struct {
	providers map[string]Provider
	order     []string // registration order, for deterministic fallback iteration
}

// NewRouter returns an empty Router ready for provider registration.
func NewRouter() *Router {
	return &Router{
		providers: make(map[string]Provider),
	}
}

// Register adds a provider under the given name. Registering the same name
// twice replaces the provider but does not duplicate its position in the
// registration order.
func (r *Router) Register(name string, p Provider) {
	if _, exists := r.providers[name]; !exists {
		r.order = append(r.order, name)
	}
	r.providers[name] = p
}

// Select picks a healthy provider, preferring names in `preferred` (in
// order) before falling back to registration order, and returns a
// RouteDecision documenting why. Returns an error only if no provider in
// the registry is healthy.
func (r *Router) Select(taskType string, preferred []string) (Provider, RouteDecision, error) {
	decision := RouteDecision{
		TaskType: taskType,
		Excluded: make(map[string]string),
	}

	seen := make(map[string]bool)
	candidates := make([]string, 0, len(preferred)+len(r.order))
	for _, name := range preferred {
		if seen[name] {
			continue
		}
		seen[name] = true
		candidates = append(candidates, name)
	}
	for _, name := range r.order {
		if seen[name] {
			continue
		}
		seen[name] = true
		candidates = append(candidates, name)
	}
	decision.Candidates = candidates

	for _, name := range candidates {
		p, ok := r.providers[name]
		if !ok {
			decision.Excluded[name] = "not registered"
			continue
		}

		health, err := p.Health()
		if err != nil {
			decision.Excluded[name] = fmt.Sprintf("health check error: %v", err)
			continue
		}
		if !health.Available {
			decision.Excluded[name] = fmt.Sprintf("unhealthy: %s", health.Reason)
			continue
		}

		decision.Selected = name
		return p, decision, nil
	}

	return nil, decision, fmt.Errorf("no healthy provider available for task type %q among %d candidate(s)", taskType, len(candidates))
}
