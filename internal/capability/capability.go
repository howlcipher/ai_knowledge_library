// Package capability holds the single source of truth (in Go) for the
// framework's capability enum. The enum itself is defined canonically in
// schemas/capability.schema.json; this map is a verbatim copy of that
// schema's enum values, kept here so every Go package that needs to check
// "is this a known capability string" (manifest validation, task request
// validation, etc.) shares one definition instead of re-declaring it.
package capability

// Valid enumerates every capability string recognized by the framework,
// matching schemas/capability.schema.json exactly.
var Valid = map[string]bool{
	"filesystem:none":           true,
	"filesystem:repository":     true,
	"filesystem:explicit_paths": true,
	"filesystem:user_approved":  true,
	"network:none":              true,
	"network:public":            true,
	"network:allowlist":         true,
	"network:user_approved":     true,
	"process:none":              true,
	"process:test_only":         true,
	"process:project_commands":  true,
	"process:user_approved":     true,
	"browser:none":              true,
	"browser:read_only":         true,
	"browser:project":           true,
	"browser:user_approved":     true,
	"git:read":                  true,
	"git:edit":                  true,
	"git:commit":                true,
	"git:push":                  true,
	"database:none":             true,
	"database:project":          true,
	"database:user_approved":    true,
	"secrets:none":              true,
	"secrets:named_reference":   true,
}

// IsKnown reports whether c is one of the framework's recognized capability
// strings.
func IsKnown(c string) bool {
	return Valid[c]
}
