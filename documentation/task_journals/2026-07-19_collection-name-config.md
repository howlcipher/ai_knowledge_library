# Task Journal: Improvement 16 — Pass the configured collection name to the vector store

## Summary

- **Task:** improvements.md item 16, "Pass the configured collection name to the vector store"
- **Status:** In progress
- **Started:** 2026-07-19
- **Agent and model:** Claude Code / Sonnet 5 (orchestrator) delegating to Antigravity CLI

## Pre-Flight Re-Evaluation

- **Model choice:** Delegate implementation to Antigravity CLI (`agy models` live: Gemini 3.5 Flash tiers, Gemini 3.1 Pro tiers, GPT-OSS 120B all available; try Gemini 3.5 Flash Medium first). Orchestration, verification, and commit stay in this Claude session.
- **Re-evaluation found the filed premise incomplete.** The item as filed says only `VectorStoreFactory.get_store()` ignores `indexing.collection_name`. Live investigation found a deeper root cause: `AppSettings` (src/infrastructure/config_loader.py) has no `indexing` field at all, and `model_config` sets `extra="ignore"`, so `default_loader.config = self.settings.model_dump()` silently drops the entire `indexing:` YAML block before `ConfigLoader.get("indexing", {})` or `load_config()` ever return it — confirmed live: writing `indexing.collection_name: test_custom` into a temp settings.yaml and loading it via `ConfigLoader` returns `MISSING`. This affects not just `collection_name` but its siblings `max_chunk_length` and `batch_size` too (same dead config path in `VectorIndexBuilder.__init__`). Fix must add an `IndexingSettings` pydantic model, not just rewire the factory.
- **Skills routed:** `software_development` (general implementation), `quality_assurance` (test design for the new pydantic field and factory behavior).
- **Free tools:** none needed beyond what's already installed (pytest, existing test patterns in `tests/`).

## Plan

- [ ] Add `IndexingSettings` pydantic model to `src/infrastructure/config_loader.py` (fields: `collection_name: str = "ai_library_knowledge"`, `max_chunk_length: int = 1000`, `batch_size: int = 100`) and add `indexing: IndexingSettings = IndexingSettings()` to `AppSettings`.
- [ ] Fix `VectorStoreFactory.get_store()` (src/infrastructure/vector_store_factory.py) to read `default_loader.get("indexing", {}).get("collection_name", "ai_library_knowledge")` and pass it to `ChromaVectorStore(collection_name=...)`. Leave the `pgvector` branch unchanged (no collection concept there; that's issues item 17's territory).
- [ ] Remove `VectorIndexBuilder`'s dead duplicate `self.collection_name` field in `src/infrastructure/build_vector_index.py` (confirmed unused anywhere else in the file) since the store now resolves it itself. Builder's `max_chunk_len`/`batch_size` reads stay (now correctly reachable once `IndexingSettings` exists).
- [ ] Add/update tests: config loader round-trips `indexing.collection_name` from YAML; `VectorStoreFactory.get_store()` returns a Chroma store with the configured collection name (and the default when unset).
- [ ] Run `make test-changed` then `make test`, review diff, commit, update backlog, delete this journal.

## Progress Log

- 2026-07-19 — Journal opened, root cause confirmed live (indexing section dropped by pydantic `extra="ignore"`), delegation brief being prepared.

## Next Step

Delegate the fix (brief covering config_loader.py, vector_store_factory.py, build_vector_index.py, and tests) to Antigravity CLI, then review the diff with `git status`/`git diff` before trusting any summary.
