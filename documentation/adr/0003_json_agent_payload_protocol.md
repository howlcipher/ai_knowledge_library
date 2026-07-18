# ADR 0003: JSON Payload Protocol for the Tiered 3 Pass Agent Pipeline

## Status

Accepted (2026-07-17)

## Context

The multi agent pipeline (Tier 3 drafting, Tier 2 peer review, Tier 1 synthesis) passed raw Markdown between agents. Markdown carries no machine readable state: pass number, tier, critique findings, and verdicts lived implicitly in prose, which breaks once Go tooling joins Python in consuming pipeline output. A rigid, language agnostic envelope is required, plus agent instructions strict enough to eliminate conversational filler around the JSON.

## Decision

Adopt a single `AgentTaskPayload` envelope (JSON Schema 2020-12, `config/schemas/agent_task_payload.schema.json`) for all three passes, with per pass mutation rights enforced by a code level validation gate, and a shared verbatim Output Contract block appended to every tier system prompt. Details in `documentation/multi_agent_payload_protocol.md`.

Alternatives evaluated:

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| JSON Schema 2020-12 | Conditional tier and pass constraints, best current tooling (`jsonschema` 4.x, `santhosh-tekuri/jsonschema/v6` in Go) | Older Go validators (gojsonschema) stop at draft-07 | Chosen |
| JSON Schema draft-07 | Widest legacy validator support | No clean conditional applicator model; loses schema enforced tier pairing | Rejected |
| Protobuf | Strongest typing, codegen for Python and Go | Binary payloads defeat LLM emission (models output text), poor human debugging | Rejected |
| Pydantic models as source of truth | Ergonomic in Python, can export schema | Go side becomes a second class consumer of a generated artifact; Python centric drift risk | Rejected |
| One schema per pass (three schemas) | Tighter per pass required fields | Triples maintenance, complicates Go structs and storage; mutation matrix in the gate covers the same ground | Rejected |

Envelope over per pass schemas: a single struct in Go and a single model in Python, with the gate enforcing pass specific rules the schema cannot express (byte for byte immutability, hash verification).

## Consequences

1. Every tier boundary gains a zero trust gate: parse, schema validate, hash check, mutation diff, bounded retry. Malformed or filler wrapped model output is caught by code, not by the next agent.
2. Markdown remains human readable inside `content.body`; no base64.
3. `pipeline.attempt` and the structured `error` object make schema failure rates a measurable telemetry dimension per model.
4. Go consumers need `santhosh-tekuri/jsonschema/v6` (2020-12); gojsonschema is not an option.
5. Schema changes require a semver bump and a matching update to the tier prompts and the test suite; `tests/test_agent_payload_schema.py` pins examples to the schema to catch drift.
