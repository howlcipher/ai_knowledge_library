# Task Journal: Rebuild the vector index

## Summary

- **Task:** Improvement #1 — Rebuild the vector index
- **Status:** Complete
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5 (session model)

## Pre-Flight Re-Evaluation

- **Model choice:** Session is already running Fable 5; the task is a script run plus spot checks, so no delegation needed and no cheaper switch is worth the overhead. Ollama is up with `qwen3:30b-instruct`, `qwen2.5vl:7b`, `nomic-embed-text` available.
- **Skills routed:** `test_and_verify` (verification loop), `commit_and_changelog` (finish loop). No domain skill applies to an index rebuild.
- **Free tools:** chromadb (already a project dependency) via `src/infrastructure/build_vector_index.py`; no new installs.

## Plan

- [x] Confirm Python environment that can import chromadb and src package (`testenv/bin/python`, chromadb 1.5.9)
- [x] Run `build_vector_index.py` (fresh build; no prior `.chroma` existed)
- [x] Spot check queries: security → `cyber_security`, crash triage → `defensive_debugging`, Terraform/K8s → `devops_sre`, resume → `career_assistant`
- [x] Ensure `.chroma/` is git-ignored (already covered by existing `.gitignore` lines 21-22)
- [x] Commit, update improvements.md status, push

## Progress Log

- 2026-07-18 — Journal opened. Verified Ollama up; no existing `.chroma` directory (index was never built after the glob fix), so this was a fresh build. ChromaDB uses its default local ONNX embedding model (no Ollama dependency for indexing).
- 2026-07-18 — First build indexed 410 chunks but included the `docs/` GitHub Pages mirror (paths like `docs/documentation/**` and `docs/.agents/**` pass the `.agents`/`documentation` substring filter), so spot checks returned the same file three times. Added `docs` to `PRUNED_DIRS` in `build_vector_index.py`, deleted `.chroma`, rebuilt: 219 chunks, all canonical, all four spot-check queries route correctly.
- 2026-07-18 — Two findings recorded as new backlog items: #3 (rebuilds are upsert-only and strand stale chunk ids; this run needed a manual `rm -rf .chroma`) and #14 (`make docs` uses `cp -r` into an existing directory, so the mirror self-nests: `docs/documentation/documentation/**` and `docs/.agents/.agents/**` are committed today). Backlog renumbered accordingly; item 1 marked Done.

## Next Step

None — task complete. Next backlog item is #2 (ignore build artifacts and local state in git).
