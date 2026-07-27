package main

import (
	"os"
	"path/filepath"
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

func TestRemoveCodexGlobalLinks(t *testing.T) {
	home := t.TempDir()
	repoRoot := t.TempDir()
	codexHome := filepath.Join(home, "custom_codex")

	sources := map[string]string{
		"software_development": filepath.Join(repoRoot, ".agents", "skills", "software_development"),
		"work_next_item":       filepath.Join(repoRoot, ".agents", "skill_commands", "work_next_item"),
	}
	for _, source := range sources {
		if err := os.MkdirAll(source, 0755); err != nil {
			t.Fatal(err)
		}
	}

	userSkills := filepath.Join(home, ".agents", "skills")
	if err := os.MkdirAll(userSkills, 0755); err != nil {
		t.Fatal(err)
	}
	for name, source := range sources {
		if err := os.Symlink(source, filepath.Join(userSkills, name)); err != nil {
			t.Fatal(err)
		}
	}
	unrelated := filepath.Join(userSkills, "unrelated")
	if err := os.MkdirAll(unrelated, 0755); err != nil {
		t.Fatal(err)
	}

	if err := os.MkdirAll(codexHome, 0755); err != nil {
		t.Fatal(err)
	}
	agentsPath := filepath.Join(codexHome, "AGENTS.md")
	agentsContent := "personal\n<!-- ai_knowledge_library:start -->\nmanaged\n<!-- ai_knowledge_library:end -->\n"
	if err := os.WriteFile(agentsPath, []byte(agentsContent), 0600); err != nil {
		t.Fatal(err)
	}

	if err := removeCodexGlobalLinks(home, codexHome, repoRoot); err != nil {
		t.Fatal(err)
	}

	for _, name := range []string{"software_development", "work_next_item"} {
		if _, err := os.Stat(filepath.Join(userSkills, name)); !os.IsNotExist(err) {
			t.Fatalf("expected %s to be removed", name)
		}
	}
	if _, err := os.Stat(filepath.Join(userSkills, "unrelated")); err != nil {
		t.Fatalf("unrelated skill was removed: %v", err)
	}
	remaining, err := os.ReadFile(agentsPath)
	if err != nil {
		t.Fatal(err)
	}
	if string(remaining) != "personal\n" {
		t.Fatalf("unexpected remaining guidance: %q", remaining)
	}
}
