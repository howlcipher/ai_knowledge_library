# Task Journal: Make vector index rebuilds idempotent

## Summary

- **Task:** Improvement #4 — Make vector index rebuilds idempotent
- **Status:** Complete
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5

## Pre-Flight Re-Evaluation

- **Model choice:** Session is already running Fable 5 on the Claude Pro subscription. The backlog suggests Haiku 4.5, but delegating this small edit to a subagent would cost more overhead than doing it inline, so proceeding with the session model. Ollama is up (`qwen3:30b-instruct` available) but not needed — no LLM calls in this task.
- **Skills routed:** `software_development` (tier 1, defensive error handling), `test_and_verify` (tier 1, prove idempotency by execution), `database_management` (tier 2, idempotency and short transactions).
- **Free tools:** chromadb CLI/client already installed via the project venv; no new installs needed.

## Plan

- [x] Add an abstract `reset()` to `BaseVectorStore`
- [x] Chroma backend: `reset()` drops the collection if it exists (recreated lazily by `upsert`)
- [x] PgVector backend: `reset()` truncates the `documents` table (its `upsert` is a plain INSERT, so reruns duplicated rows too)
- [x] `build_vector_index.py`: call `store.reset()` after `init_db()` before inserting
- [x] Verify: rebuild twice → same chunk count; add a temp md file, build, delete it, rebuild → its chunks are gone and the count returns to baseline
- [x] Update improvements.md status, changelog, commit, push

## Findings (candidate new backlog items)

- `indexing.collection_name` from config is read by `VectorIndexBuilder` but never passed to `ChromaVectorStore` (factory constructs it with the hardcoded default). Config value silently ignored.
- `PgVectorStore.upsert` ignores `ids`, does a plain `INSERT` with no unique constraint — it is not an upsert. `reset()` masks this for full rebuilds, but incremental use would still duplicate.

## Progress Log

- 2026-07-18 — Journal opened; code read (`build_vector_index.py`, both backends, factory, base). Root cause confirmed: builder only upserts, chunk ids `<path>_<n>` strand stale entries; pgvector path duplicates rows on every run.
- 2026-07-18 — Implemented `reset()` (abstract in base, collection drop in Chroma, `TRUNCATE ... RESTART IDENTITY` in pgvector) and wired it into `insert_chunks()` after `init_db()`. No other `BaseVectorStore` subclasses exist (grep confirmed), so the new abstract method breaks nothing.
- 2026-07-18 — Verified: two consecutive rebuilds both insert a stable 230 chunks (baseline was 219 from the last build; the delta is new docs written since). Probe test: added `documentation/temp_idempotency_probe.md`, rebuild → 231 chunks and probe id present; deleted it, plain rebuild → 230 chunks, probe id absent, marker absent from query results. Security spot-check query still routes `cyber_security` first. Pgvector path is compile-checked only (no live Postgres on this host). Full suite: 98 passed.
- 2026-07-18 — Two findings recorded as new backlog items #16 (`indexing.collection_name` config is never passed to the store — factory hardcodes the default) and #17 (pgvector `upsert` is a plain INSERT that ignores `ids`); old items 16–21 renumbered to 18–23 with cross references in the Completed section updated. Changelog updated under Fixed and mirrored to `docs/change_log.md` (item 14 automation still pending).

## Next Step

None — task complete. Next backlog item is #5 (preflight the provider before a run).
