package project

import (
	"path/filepath"
	"testing"
)

// TestLoadManifest_ExampleManifests ensures every example manifest shipped
// under examples/manifests/ is a legitimate, valid .ai-project.toml file
// per the current validation rules.
func TestLoadManifest_ExampleManifests(t *testing.T) {
	pattern := filepath.Join("..", "..", "examples", "manifests", "*.toml")
	matches, err := filepath.Glob(pattern)
	if err != nil {
		t.Fatalf("failed to glob example manifests: %v", err)
	}
	if len(matches) == 0 {
		t.Fatalf("no example manifests found matching %s", pattern)
	}

	for _, path := range matches {
		path := path
		t.Run(filepath.Base(path), func(t *testing.T) {
			m, err := LoadManifest(path)
			if err != nil {
				t.Fatalf("expected %s to be a valid manifest, got error: %v", path, err)
			}
			if m.Name == "" {
				t.Fatalf("expected %s to have a non-empty name", path)
			}
		})
	}
}
