package project

import (
	"fmt"
	"io"
	"os"

	"github.com/pelletier/go-toml/v2"
)

// Manifest represents the structure of .ai-project.toml
type Manifest struct {
	SchemaVersion int                 `toml:"schema_version"`
	Name          string              `toml:"name"`
	ProjectType   []string            `toml:"project_type,omitempty"`
	Skills        []string            `toml:"skills,omitempty"`
	Context       ContextBlock        `toml:"context,omitempty"`
	Commands      map[string][]string `toml:"commands,omitempty"`
	Security      SecurityBlock       `toml:"security,omitempty"`
	Routing       map[string][]string `toml:"routing,omitempty"`
}

type ContextBlock struct {
	Include []string `toml:"include,omitempty"`
	Exclude []string `toml:"exclude,omitempty"`
}

type SecurityBlock struct {
	Capabilities []string `toml:"capabilities,omitempty"`
}

// LoadManifest reads and parses a project manifest from the given path.
func LoadManifest(path string) (*Manifest, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("failed to open manifest: %w", err)
	}
	defer file.Close()
	return parseManifest(file)
}

func parseManifest(r io.Reader) (*Manifest, error) {
	decoder := toml.NewDecoder(r)
	decoder.DisallowUnknownFields() // For strict validation of known blocks? Wait, the blueprint says: "tests covering ... forward-compatible unknown fields". So we should NOT disallow unknown fields.

	// Recreating decoder to allow unknown fields.
	decoder = toml.NewDecoder(r)

	var m Manifest
	if err := decoder.Decode(&m); err != nil {
		return nil, fmt.Errorf("failed to parse manifest: %w", err)
	}

	if err := validateManifest(&m); err != nil {
		return nil, err
	}

	return &m, nil
}

func validateManifest(m *Manifest) error {
	if m.SchemaVersion != 1 {
		return fmt.Errorf("invalid schema_version: expected 1, got %d", m.SchemaVersion)
	}
	if m.Name == "" {
		return fmt.Errorf("manifest is missing required field 'name'")
	}

	// Validate capabilities
	validCaps := map[string]bool{
		"filesystem:none": true, "filesystem:repository": true, "filesystem:explicit_paths": true, "filesystem:user_approved": true,
		"network:none": true, "network:public": true, "network:allowlist": true, "network:user_approved": true,
		"process:none": true, "process:test_only": true, "process:project_commands": true, "process:user_approved": true,
		"browser:none": true, "browser:read_only": true, "browser:project": true, "browser:user_approved": true,
		"git:read": true, "git:edit": true, "git:commit": true, "git:push": true,
		"database:none": true, "database:project": true, "database:user_approved": true,
		"secrets:none": true, "secrets:named_reference": true,
	}

	for _, cap := range m.Security.Capabilities {
		if !validCaps[cap] {
			return fmt.Errorf("unknown capability: %s", cap)
		}
	}

	return nil
}
