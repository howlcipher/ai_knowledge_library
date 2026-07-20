# Task Journal: Orchestrator leaks MCP server subprocesses across instances (issues.md bug 5)

## Summary

- **Task:** issues.md bug 5 — `Orchestrator` spawns real MCP subprocesses (`SyncMCPClient`) in `__init__` and only tears them down via `atexit.register(self.shutdown)`, never mid-process. Both `tests/test_orchestrator.py` (5 constructions) and `tests/test_provider_preflight.py` (2 constructions) construct `Orchestrator()` directly with no teardown, so every test run leaks live subprocesses (verified live 2026-07-20: `config/settings.yaml`'s `active_mcps: [memory, fetch]` currently matches the `fetch` entry in `mcp_servers`, spawning `uvx mcp-server-fetch` per construction — the bug report's "server-memory" example predates a config edit but the same construction-time-spawn/no-teardown mechanism reproduces today).
- **Status:** In progress
- **Started:** 2026-07-20
- **Agent and model:** Claude Code / Sonnet 5 (orchestrator), delegating implementation

## Pre-Flight Re-Evaluation

- **Model choice:** Delegating to Antigravity CLI, Gemini 3.1 Pro (Low first, escalate to High if the diff is wrong/incomplete) — matches the item's suggested "Gemini 3 Pro" tier and current `agy models` output. GPT-OSS 120B as fallback if Gemini tiers hit shared quota.
- **Skills routed:** `test_and_verify` (fixture/teardown design), `defensive_debugging` (root-causing the leak before fixing).
- **Free tools:** none new needed; existing `pytest` fixture mechanism is sufficient.

## Plan

- [ ] Write delegation brief: add a `tests/conftest.py` fixture (e.g. `orchestrator_factory` or an autouse teardown) that tracks any `Orchestrator` instances created via a shared fixture and calls `.shutdown()` on teardown; convert the 7 direct `Orchestrator()` call sites in `tests/test_orchestrator.py` and `tests/test_provider_preflight.py` to use it.
- [ ] Delegate to agy.
- [ ] Review diff, run `make test-changed` then `make test`.
- [ ] Update issues.md bug 5 row/detail to Done, commit, delete this journal, push.

## Progress Log

- 2026-07-20 — Re-verified bug live: `atexit`-only shutdown confirmed in `src/core/orchestrator.py:239-244`; no conftest.py exists in the repo; `config/settings.yaml` has a live `mcp_servers.fetch` entry matched by `active_mcps`, confirming real subprocess spawn on every `Orchestrator()` construction in tests. Opened journal, about to delegate.
- 2026-07-20 — Delegated to Antigravity CLI / Gemini 3.1 Pro (Low): failed immediately with "Individual quota reached... Resets in 3h13m28s". `git status` confirmed zero partial edits. Retried with GPT-OSS 120B (Medium), running in background.

## Next Step

Await GPT-OSS 120B delegation result; verify `git diff` against the brief (tests/conftest.py new, tests/test_orchestrator.py, tests/test_provider_preflight.py only), run `make test-changed` then `make test`.
