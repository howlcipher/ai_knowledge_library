package main

import (
	"os"
	"testing"
)

func TestIsRepoRoot_True(t *testing.T) {
	// Create a dummy .agents dir to simulate being in the repo root
	err := os.MkdirAll(".agents", 0755)
	if err != nil {
		t.Fatalf("Failed to create dummy .agents dir: %v", err)
	}
	defer os.RemoveAll(".agents")

	installer := NewInstaller()
	if !installer.IsRepoRoot() {
		t.Errorf("Expected IsRepoRoot to return true when .agents exists")
	}
}

func TestNewInstaller_Defaults(t *testing.T) {
	installer := NewInstaller()
	if installer.RepoURL != DefaultRepoURL {
		t.Errorf("Expected RepoURL to be %s, got %s", DefaultRepoURL, installer.RepoURL)
	}
	if installer.DestPath == "" {
		t.Errorf("Expected DestPath to be populated, got empty string")
	}
}
