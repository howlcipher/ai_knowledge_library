# Task Journal: Bounded Execution and Pre-Execution Human Authority Gating

## Summary

- **Task:** Bug #11 — Consequential execution is not mechanically separated from proposal/implementation, and approval can be mistaken for completion & Improvement #55 — HowlChangeOps bounded execution handoff
- **Status:** In progress
- **Started:** 2026-08-20
- **Agent and model:** Antigravity CLI / Gemini 3.7 Flash

## Pre-Flight Re-Evaluation

- **Model choice:** Gemini 3.7 Flash (High) - high architectural and reasoning capacity for security and authority boundary verification.
- **Skills routed:** `cyber_security`, `defensive_debugging`, `quality_assurance`, `test_and_verify`, `commit_and_changelog`, `architectural_guardrails`, `systems_logic`, `howlframe-app-development`.
- **Free tools:** `howlchangeops` (canonical bounded executor at `/run/media/system/tallgeese/dev/howlchangeops`), `howlframe` (VM runtime), `git`, `pytest`, `flake8`, `bandit`, `slopslint`.

## Plan

- [ ] 1. Reproduce authority gap (unrestricted agent execution before human boundary) and false completion bug in deterministic tests.
- [ ] 2. Update `issues.md` (Bug #11) and `improvements.md` (Improvement #55).
- [ ] 3. Fix authority ordering: model proposed/executable actions and gate consequential actions before implementation agent execution.
- [ ] 4. Fix lifecycle completion: require execution evidence/receipts before transitioning to COMPLETE.
- [ ] 5. Implement narrow `HowlChangeOpsExecutor` adapter with safe subprocess invocation, action validation, and receipt mapping.
- [ ] 6. Enforce trust provenance: prevent forged receipts and decisions by agents.
- [ ] 7. Add full test suite covering success, failures, stale evidence, unsupported actions, forged receipts, and status UX.
- [ ] 8. Dogfood safe real execution against a temporary local Git repository.
- [ ] 9. Verify full test suite, linting, SAST, and hygiene policy.

## Progress Log

- 2026-08-20 14:50 — Started task, inspected HowlPlane orchestrator, launcher, human boundary lifecycle, and HowlChangeOps contracts. Verified baseline test suites clean.

## Next Step

Reproduce the pre-execution human boundary gap and approval-only false completion with deterministic tests.
