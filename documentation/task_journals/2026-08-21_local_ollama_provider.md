# Task Journal: Milestone #58 — Local AI Worker + Safe Continuous Dogfooding

## Summary

- **Task:** #58 — Local Ollama (qwen2.5-coder:7b-instruct) provider backend, dogfood resume-scope fix, read-only status command, memory-safe/concurrency-safe local routing, bounded local-only continuation.
- **Status:** In progress
- **Started:** 2026-08-21
- **Agent and model:** Devin CLI

## Pre-Flight Re-Evaluation

- **Model choice:** Devin CLI (this session).
- **Skills routed:** `software_development`, `test_and_verify`, `systems_logic`, `resume_task`.
- **Free tools:** pytest, go test, flake8, bandit, slopslint, gh, ollama (installed this session, real).

## Plan

- [x] Phase 0: Verify main baseline (c6aab83, CI green), branch `feat/local-ollama-provider`.
- [ ] Phase 1: Fix `ai dogfood --resume` scope expansion bug; add `ai dogfood --status`.
- [ ] Phase 2-4: Ollama discovery + real `local_ollama`/`ollama_local` AgentBackend.
- [ ] Phase 5-8: Memory guard, concurrency lock, context budget.
- [ ] Phase 9-13: Tier-3 eligibility gating, local-only continuation budget, campaign state.
- [ ] Phase 18: CI-safe fake-backed tests for all required scenarios.
- [ ] Local verification: pytest/go/flake8/bandit/slopslint.
- [ ] Commit, push, PR, green CI, merge.
- [ ] Phase 19-21: Real Ollama install + pull + real local dogfood task.
- [ ] Phase 23-24: Docs + readiness check.

## Progress Log

- 2026-08-21 — Verified main at c6aab83 with green CI (Run Tests, Lint and Security, Docs all success). No in-flight journals for #58. Explored `provider_pool.py`, `agent_execution.py`, `marathon.py`, `campaign_state.py`, `router.py`, `locking.py`, `agent_registry.py`, `cli.py`. Found existing `local_ollama` AgentProfile/backend scaffolding (tier_3, free_local) already present from earlier work, but backend was a naive `ollama run <prompt>` subprocess with no discovery/memory/concurrency/context-budget logic. Decided to keep canonical agent_id `local_ollama` (deeply referenced across registry/tests) and add `ollama_local` as an alias, rather than a disruptive rename.

- 2026-08-21 — Implemented resume-scope fix (`requested_benchmarks`/`scope_extensions` in `DurableCampaignState`, restored-not-expanded on resume) and read-only `ai dogfood --status`. Implemented real `OllamaLocalBackend` (discovery via `diagnose_ollama`, HTTP inference, memory guard, `LocalInferenceLock` single-flight concurrency, 8192-token context budget) replacing the naive subprocess stub, keeping canonical agent_id `local_ollama` with `ollama_local` as an alias. Added `RESOURCE_CONSTRAINED` status and non-exhaustion classification for local failures in `provider_pool.py`. Added `is_task_local_eligible` Tier-3 risk gating threaded through `select_candidates(..., task=...)` at all call sites (engine.py x2, marathon.py x2). Added bounded `_run_local_only_continuation` with durable `campaign_state.local_model` counters. Added `ai local setup`. Fixed one pre-existing test (`test_scenario_5_all_providers_exhausted_clean_stop`) whose fixture assumed the old (incorrect) local-quota-exhaustion behavior. Added `tests/test_local_ollama_provider.py` (29 tests, all fake-backed). Full verification green: 592 Python tests, Go tests, flake8 (E9/F63/F7/F82) clean, bandit clean, slopslint clean (14/14, 29/29 at ceiling). Wrote `documentation/LOCAL_MODEL.md`, cross-linked from README, and closed backlog item #58 in `improvements.md`.

## Next Step

Commit and push `feat/local-ollama-provider`, open PR, get CI green, merge, then perform the real Ollama install/pull/inference on this machine (Phase 19-21) and update the final report.
