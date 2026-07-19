# Task Journal: Emit gate failures into telemetry

## Summary

- **Task:** improvements.md item 12 — Emit gate failures into telemetry
- **Status:** In progress
- **Started:** 2026-07-19
- **Agent and model:** Claude Code / Sonnet 5 (orchestration), delegate TBD

## Pre-Flight Re-Evaluation

- **Model choice:** Delegating implementation to Antigravity CLI (Gemini 3.5 Flash Medium, live per `agy models`) per Working Protocol step 2 — small, well-bounded change, cheapest capable model.
- **Skills routed:** `software_development` (general implementation), `quality_assurance` (test design), `defensive_debugging` (telemetry/observability angle).
- **Free tools:** none new needed; using existing `src/infrastructure/telemetry_logger.py` (SQLite) and pytest.

## Plan

- [x] Re-read `src/core/validation_gate.py` and `src/infrastructure/telemetry_logger.py` to confirm current shape.
- [ ] Add `log_gate_failure(model, pass_number, attempt, stage, error_message)` to `telemetry_logger.py` (new `gate_failures` table), matching the `error` object structure from `documentation/multi_agent_payload_protocol.md` line 162.
- [ ] Wire `ValidationGate.run` with an optional `on_failure` callback invoked per failed attempt (stage + errors), and have `src/core/orchestrator.py`'s `run_payload_loop` pass a callback that calls `log_gate_failure` with the current tier's model name.
- [ ] Add/update tests: `tests/test_telemetry_logger.py` (new table + log function), `tests/test_validation_gate.py` (callback invoked on failed attempts, not on success).
- [ ] Run `make test-changed` then full `make test`.
- [ ] Update improvements.md row 12 to Done, delete this journal, commit, push.

## Progress Log

- 2026-07-19 — Journal opened, re-evaluation confirmed item still relevant: `validation_gate.py`'s `run()` prints failures at line 257-260 but never calls telemetry_logger, confirmed live. Delegating implementation now.

## Next Step

Delegate the implementation brief to Antigravity CLI (`agy`), then review the diff.
