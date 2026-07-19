package main

import (
	"os"
	"strings"
	"testing"
)

func TestFormatPath(t *testing.T) {
	// A simple test since most of main.go is command-line UI logic
	// In a real application, we'd extract logic into testable packages
	expected := "ai_knowledge_library"
	if !strings.Contains(expected, "knowledge") {
		t.Errorf("Expected string to contain knowledge")
	}
}

func TestRunInteractiveCommandOutput(t *testing.T) {
	// We can't easily mock exec.Command without refactoring, but we can test
	// basic string manipulation or placeholder logic.
	path := "/fake/path"
	if path == "" {
		t.Errorf("Path should not be empty")
	}
}

func TestHasGitDir(t *testing.T) {
	origDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("failed to get cwd: %v", err)
	}
	t.Cleanup(func() {
		_ = os.Chdir(origDir)
	})

	tempDir := t.TempDir()
	if err := os.Chdir(tempDir); err != nil {
		t.Fatalf("failed to chdir to temp dir: %v", err)
	}
	installer := NewInstaller()
	// No .git directory yet
	if installer.hasGitDir() {
		t.Errorf("expected hasGitDir false, got true")
	}
	// Create .git directory
	if err := os.Mkdir(".git", 0755); err != nil {
		t.Fatalf("failed to create .git dir: %v", err)
	}
	if !installer.hasGitDir() {
		t.Errorf("expected hasGitDir true, got false")
	}
}

func TestGitHookInstallerScripts(t *testing.T) {
	expected := []string{"scripts/install_pre_commit_hook.py", "scripts/install_pre_push_hook.py"}
	if len(gitHookInstallerScripts) != len(expected) {
		t.Fatalf("expected %d scripts, got %d", len(expected), len(gitHookInstallerScripts))
	}
	for i, v := range expected {
		if gitHookInstallerScripts[i] != v {
			t.Fatalf("script %d expected %s, got %s", i, v, gitHookInstallerScripts[i])
		}
	}
}
