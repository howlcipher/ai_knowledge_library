package runtime

// FailureClass is the shared failure taxonomy every provider adapter must
// map its errors into, per blueprint section 8.3 and
// schemas/failure-class.schema.json.
type FailureClass string

const (
	FailureUsageLimit           FailureClass = "usage_limit"
	FailureAuthentication       FailureClass = "authentication"
	FailureModelUnavailable     FailureClass = "model_unavailable"
	FailurePermissionOrApproval FailureClass = "permission_or_approval"
	FailureNetworkTransient     FailureClass = "network_transient"
	FailureProviderTransient    FailureClass = "provider_transient"
	FailureCancelled            FailureClass = "cancelled"
	FailureTimeout              FailureClass = "timeout"
	FailureTaskFailure          FailureClass = "task_failure"
	FailureInvalidOutput        FailureClass = "invalid_output"
	FailureSecurityDenied       FailureClass = "security_denied"
	FailureWorkspaceUnsafe      FailureClass = "workspace_unsafe"
	FailureUnknown              FailureClass = "unknown"
)

// validFailureClasses backs IsValid; kept as a package-level map so
// membership checks are O(1) and the enum has one canonical listing.
var validFailureClasses = map[FailureClass]bool{
	FailureUsageLimit:           true,
	FailureAuthentication:       true,
	FailureModelUnavailable:     true,
	FailurePermissionOrApproval: true,
	FailureNetworkTransient:     true,
	FailureProviderTransient:    true,
	FailureCancelled:            true,
	FailureTimeout:              true,
	FailureTaskFailure:          true,
	FailureInvalidOutput:        true,
	FailureSecurityDenied:       true,
	FailureWorkspaceUnsafe:      true,
	FailureUnknown:              true,
}

// IsValid reports whether f is one of the 13 recognized failure taxonomy
// values.
func (f FailureClass) IsValid() bool {
	return validFailureClasses[f]
}

// RetriableViaFallback reports whether this failure class should trigger
// automatic fallback to another provider.
//
// Per blueprint section 8.3: "Only availability and infrastructure failures
// trigger automatic fallback by default. A normal task failure must not be
// silently treated as a provider outage." That is a deliberate narrowing:
// classes like task_failure, invalid_output, security_denied, and
// workspace_unsafe are about the task or the sandbox, not the provider being
// unreachable, so silently retrying them on a different provider would mask
// real problems (a broken task, a denied capability, an unsafe workspace)
// as if they were transient outages. Only the four classes below describe
// the provider itself being unavailable or infrastructure being flaky, so
// only those are safe to retry automatically.
func (f FailureClass) RetriableViaFallback() bool {
	switch f {
	case FailureModelUnavailable, FailureNetworkTransient, FailureProviderTransient, FailureTimeout:
		return true
	default:
		return false
	}
}
