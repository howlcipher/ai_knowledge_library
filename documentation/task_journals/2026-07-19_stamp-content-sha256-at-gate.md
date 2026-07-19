# Task Journal: Stamp `content.sha256` in code at the gate (improvements.md #31)

## Summary

- **Task:** improvements.md #31 — stop asking agents to compute SHA-256 by hand; have `ValidationGate` recompute and stamp `content.sha256` on write passes (1, 3) and keep verifying it on the read-only pass (2).
- **Status:** In progress
- **Started:** 2026-07-19
- **Agent and model:** Claude Code / Sonnet 5 (orchestrator) delegating implementation to Antigravity CLI

## Pre-Flight Re-Evaluation

- **Re-check:** still valid. `src/core/validation_gate.py:216-218` unconditionally rejects any pass whose `content.sha256` doesn't match a code-recomputed hash, and `tier_prompts.py` still instructs Tier 3 (pass 1) and Tier 1 (pass 3) to compute the real SHA-256 by hand — an LLM cannot do this reliably. Confirmed via `grep -rn sha256 src/` — single Python implementation, no Go consumer of the gate to keep in sync.
- **Model choice:** Antigravity CLI, Gemini 3.1 Pro (High) — `agy models` currently lists Gemini 3.5 Flash/3.1 Pro tiers, Claude Sonnet/Opus 4.6, GPT-OSS 120B. This item needs precise, multi-file synchronized edits (gate logic + two prompt strings + protocol doc + tests), so picked the strongest available Gemini tier over Flash. Escalate to Claude Sonnet 4.6 via agy (bills Google subscription) if Gemini quota is exhausted or the diff needs rework.
- **Skills routed:** `software_development` (general implementation), `quality_assurance` (test design standards for the new/changed gate tests).
- **Free tools:** none new; using existing `agy` CLI and local `make test-changed` / `make test`.

## Plan

- [ ] Delegate the implementation (gate logic, tier prompts, protocol doc, schema description, tests) to Antigravity CLI.
- [ ] Review the full diff myself.
- [ ] Run `make test-changed` then `make test`.
- [ ] Fix small gaps directly or re-delegate with feedback.
- [ ] Update improvements.md #31 to Done, delete this journal, commit, push.

## Progress Log

- 2026-07-19 — Journal opened, re-evaluation confirmed, delegate model chosen.

## Next Step

Write the delegation brief and dispatch to Antigravity CLI (`agy`) with absolute file paths.
