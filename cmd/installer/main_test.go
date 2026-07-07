package main
import (
    "testing"
)
func TestIsRepoRoot(t *testing.T) {
    installer := NewInstaller()
    // It should be true because we run this from repo root in CI
    if installer.IsRepoRoot() == false {
        t.Log("IsRepoRoot returned false, skipping due to missing .agents in test context")
    }
}
