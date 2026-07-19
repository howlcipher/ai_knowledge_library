# Task Journal: Make vector index rebuilds idempotent

## Summary

- **Task:** Improvement #4 — Make vector index rebuilds idempotent
- **Status:** In progress
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5

## Pre-Flight Re-Evaluation

- **Model choice:** Session is already running Fable 5 on the Claude Pro subscription. The backlog suggests Haiku 4.5, but delegating this small edit to a subagent would cost more overhead than doing it inline, so proceeding with the session model. Ollama is up (`qwen3:30b-instruct` available) but not needed — no LLM calls in this task.
- **Skills routed:** `software_development` (tier 1, defensive error handling), `test_and_verify` (tier 1, prove idempotency by execution), `database_management` (tier 2, idempotency and short transactions).
- **Free tools:** chromadb CLI/client already installed via the project venv; no new installs needed.

## Plan

- [ ] Add an abstract `reset()` to `BaseVectorStore`
- [ ] Chroma backend: `reset()` drops the collection if it exists (recreated lazily by `upsert`)
- [ ] PgVector backend: `reset()` truncates the `documents` table (its `upsert` is a plain INSERT, so reruns duplicated rows too)
- [ ] `build_vector_index.py`: call `store.reset()` after `init_db()` before inserting
- [ ] Verify: rebuild twice → same chunk count; add a temp md file, build, delete it, rebuild → its chunks are gone and the count returns to baseline
- [ ] Update improvements.md status, changelog, commit, push

## Findings (candidate new backlog items)

- `indexing.collection_name` from config is read by `VectorIndexBuilder` but never passed to `ChromaVectorStore` (factory constructs it with the hardcoded default). Config value silently ignored.
- `PgVectorStore.upsert` ignores `ids`, does a plain `INSERT` with no unique constraint — it is not an upsert. `reset()` masks this for full rebuilds, but incremental use would still duplicate.

## Progress Log

- 2026-07-18 — Journal opened; code read (`build_vector_index.py`, both backends, factory, base). Root cause confirmed: builder only upserts, chunk ids `<path>_<n>` strand stale entries; pgvector path duplicates rows on every run.

## Next Step

Implement `reset()` in vector_store_base / chroma_backend / pgvector_backend and call it from `build_vector_index.py`.
