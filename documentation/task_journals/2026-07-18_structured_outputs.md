# Task Journal: Provider enforced structured outputs (item 8)

Copy this file to `YYYY-MM-DD_<slug>.md` before starting a task (see the Working Protocol in `improvements.md`). Update and commit it at every milestone. A fresh session resumes by reading Status, the last Progress entry, and Next Step. When the task completes, move anything durable (findings, decisions, verification evidence) into the backlog Done note, the changelog, or a proper doc, then delete the journal in the task's final commit — only in-flight tasks have a journal here.

## Summary

- **Task:** Improvement #8 — Provider enforced structured outputs
- **Status:** In progress
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5 (current session model; no in-session downgrade path)

## Pre-Flight Re-Evaluation

- **Item still valid?** Yes. Gate catches invented fields only after burning validation attempts; protocol doc Additional Recommendation 1 explicitly calls for provider-enforced structured output with the prompt contract kept as defense in depth. litellm 1.83.0 (installed) supports `response_format` json_schema and maps it to Ollama's `format` parameter.
- **Model choice:** Session runs as Fable 5; table suggested Sonnet 5. No cost difference on subscription and no in-session model switch, so proceeding. Live verification uses local Ollama (`qwen3:30b-instruct`, `qwen2.5vl:7b` available; server confirmed up via `/api/tags`).
- **Skills routed:** `software_development` (input validation at boundaries, defensive error handling), `quality_assurance` deferred to for test design, `machine_learning` reviewed via manifest description (LLM protocols).
- **Free tools:** litellm (installed) is the enforcement vehicle; Ollama structured outputs (`format` param) is the local backend. No new installs needed.

## Plan

- [ ] New `src/core/structured_output.py`: load `agent_task_payload.schema.json`, strip metadata keys providers reject (`$schema`, `$id`), return litellm `response_format` dict (`type: json_schema`, non-strict — schema has optional fields incompatible with OpenAI strict mode).
- [ ] `Agent` gains optional `response_format`, passed to `litellm.completion` when set (same pattern as `timeout`).
- [ ] `run_payload_loop` wires it into all three tier agents behind `payload_pipeline.structured_outputs` (default true) in `settings.yaml`.
- [ ] Unit tests: kwarg pass-through, omission when unset, config toggle off, helper strips metadata keys.
- [ ] Live verify against Ollama: constrained generation returns schema-valid JSON; adjust schema sanitization if Ollama rejects keywords (if/then, pattern, format).
- [ ] `make test-changed`, full `make test`, update backlog row + Done note + changelog, delete journal, commit, push.

## Progress Log

- 2026-07-18 — Journal opened. Code paths read: `orchestrator.py` (Agent kwargs pattern from item 6, `run_payload_loop` tier construction), `validation_gate.py` (gate unchanged, stays authoritative), schema, protocol doc, ADR 0003.

## Next Step

Implement `src/core/structured_output.py` and the `Agent.response_format` plumbing.
