package project

import (
	"os"
	"path/filepath"
	"testing"
)

func TestDiscoverRoot_WithManifest(t *testing.T) {
	dir := t.TempDir()

	// Create nested dirs
	nested := filepath.Join(dir, "a", "b", "c")
	if err := os.MkdirAll(nested, 0755); err != nil {
		t.Fatalf("failed to create nested dirs: %v", err)
	}

	// Create manifest at 'a'
	rootPath := filepath.Join(dir, "a")
	manifestPath := filepath.Join(rootPath, ".ai-project.toml")
	if err := os.WriteFile(manifestPath, []byte(""), 0644); err != nil {
		t.Fatalf("failed to write manifest: %v", err)
	}

	discovered, err := DiscoverRoot(nested)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if discovered != rootPath {
		t.Errorf("expected root %s, got %s", rootPath, discovered)
	}
}

func TestDiscoverRoot_WithGitFallback(t *testing.T) {
	dir := t.TempDir()

	// Create nested dirs
	nested := filepath.Join(dir, "x", "y")
	if err := os.MkdirAll(nested, 0755); err != nil {
		t.Fatalf("failed to create nested dirs: %v", err)
	}

	// Create .git at 'x'
	rootPath := filepath.Join(dir, "x")
	gitPath := filepath.Join(rootPath, ".git")
	if err := os.MkdirAll(gitPath, 0755); err != nil {
		t.Fatalf("failed to create .git: %v", err)
	}

	discovered, err := DiscoverRoot(nested)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if discovered != rootPath {
		t.Errorf("expected root %s, got %s", rootPath, discovered)
	}
}

func TestDiscoverRoot_NotFound(t *testing.T) {
	dir := t.TempDir()
	_, err := DiscoverRoot(dir)
	if err == nil {
		t.Fatalf("expected error when no root markers are found")
	}
}
