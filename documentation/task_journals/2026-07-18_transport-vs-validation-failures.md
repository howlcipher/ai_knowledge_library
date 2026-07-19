# Task Journal: Separate transport failures from validation failures

Copy this file to `YYYY-MM-DD_<slug>.md` before starting a task (see the Working Protocol in `improvements.md`). Update and commit it at every milestone. A fresh session resumes by reading Status, the last Progress entry, and Next Step. When the task completes, move anything durable (findings, decisions, verification evidence) into the backlog Done note, the changelog, or a proper doc, then delete the journal in the task's final commit — only in-flight tasks have a journal here.

## Summary

- **Task:** Improvement #7 — Separate transport failures from validation failures
- **Status:** In progress
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5

## Pre-Flight Re-Evaluation

- **Model choice:** Fable 5 (the running session). Table suggests Sonnet 5; switching or delegating mid-session would re-derive already-loaded context for no cost saving, and the task (exception taxonomy + retry semantics across gate/orchestrator boundaries) comfortably fits the current model. Available: Claude Pro (this session), Gemini Pro, local Ollama (`qwen3:30b-instruct`, `qwen2.5vl:7b`, `nomic-embed-text`).
- **Skills routed:** `defensive_debugging` (error handling protocol; defensive error handling, no internal-detail leakage), deferring to `quality_assurance`/`test_and_verify` for the test loop and `software_development` for style per its Related Skills.
- **Free tools:** nothing new needed — pytest + `make test-changed` cover the loop. Live Ollama available for an optional end-to-end probe (kill-server test) but unit tests with mocked `litellm.completion` are sufficient and deterministic.

## Item re-evaluation (still worth working? requirements sane?)

Yes. Verified in code: `Agent.generate_response` catches all exceptions and returns `None` (orchestrator.py:113-115); `run_payload_loop.call_fn` maps that to `""`; `ValidationGate.parse` scores `""` as a `parse` failure, consuming one of `max_attempts`; `build_failed_payload` then stamps `SCHEMA_VALIDATION_FAILED` / `validation_gate.parse`, masking the real transport cause. Schema's `error.code` is a free `^[A-Z0-9_]+$` pattern, so `UPSTREAM_UNAVAILABLE` is legal. Requirements unchanged and implementable as written.

## Design

- New `src/core/transport_retry.py`: `ProviderTransportError(message, model, attempts, attempt_errors)` and `call_with_transport_retry(fn, retries, backoff, sleep)` — exponential backoff (`backoff * 2**n`), collects each attempt's provider message, raises `ProviderTransportError` on exhaustion.
- `Agent.generate_response(..., raise_errors=False)`: split the try so only `litellm.completion` errors count as provider errors (re-raised when `raise_errors=True`); a telemetry-logging failure no longer discards a successful completion (latent bug found during this item).
- `run_payload_loop`: `call_fn` wraps the agent call in `call_with_transport_retry`; `gate.run` wrapped in `try/except ProviderTransportError` → persist a failed payload with `code=UPSTREAM_UNAVAILABLE`, `failure_vector=llm_transport.completion`, provider messages in `error.context.attempt_errors`, and halt without consuming validation attempts.
- `ValidationGate.build_failed_payload` gains optional `code`, `failure_vector`, `context` kwargs (defaults preserve current behavior).
- Config: `payload_pipeline.transport_retries` (default 2) and `transport_backoff` (default 2.0 s) in `settings.yaml` + `PayloadPipelineSettings`.

## Plan

- [x] Journal opened and committed
- [ ] Implement `transport_retry.py` + `Agent.raise_errors` + orchestrator wiring + gate kwargs + config
- [ ] Tests: retry helper unit tests; Agent raise/swallow/telemetry paths; orchestrator integration (dead provider → UPSTREAM_UNAVAILABLE, zero gate attempts burned; transient failure → retry succeeds); gate kwarg test
- [ ] `make test-changed`, then full `make test`
- [ ] Backlog row Done + Done note + changelog, delete journal, commit, push

## Progress Log

- 2026-07-18 — Journal opened; code paths read (orchestrator.py, validation_gate.py, schema, settings.yaml, config_loader.py); design fixed as above.

## Next Step

Implement `src/core/transport_retry.py` per the Design section, then wire orchestrator/gate/config.
