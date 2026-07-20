# Task Journal: Item 40 — README `Neural_Nodes` badge is not tied to any live metric

## Summary

- **Task:** improvements.md item 40 — `README.md`'s `Neural_Nodes` badge hardcodes `message=386`, not computed from anything live.
- **Status:** In progress
- **Started:** 2026-07-20
- **Agent and model:** Claude Code (orchestrator) / delegating implementation to Antigravity CLI

## Pre-Flight Re-Evaluation

- **Re-verified live:** `README.md` line 5 still hardcodes `message=386`. Confirmed no live-count infra exists for chunk count (no `count()` method anywhere in the vector store abstraction).
- **Root cause found (new context beyond the original item text):** `scripts/library_statistics.py`, wired into `.github/workflows/update_badges.yml` (runs on every push to main), was *supposed* to keep a badge live, but its `badge_pattern` regex targets a `Library_Size`/`color=success` badge and its fallback insertion anchor (`first_badge_line`) targets `label=AI&message=Knowledge_Library&color=blueviolet` — both predate the 2026-07-13 cyberpunk rebrand and match nothing in the current README (confirmed via grep: only `SYS_CORE`, `Neural_Nodes`, `Powered_By` badges exist now). So this automation has been a silent no-op on every push since the rebrand — no test exists for it (`find tests -iname "*badge*" -o -iname "*statistics*"` → nothing), same "untested and silently dead" pattern as issues.md bugs 1/2.
- **Decision:** rather than option (b)/(c) (decorative text or delete), repair this existing dead automation to target the real `Neural_Nodes` badge with a real metric. Chose skill count (`len(json.load(open(".agents/skills.json"))["skills"])`, currently 38) over chunk count: chunk count needs a live ChromaDB connection unavailable in a plain CI checkout; skill count is a plain, already-committed, already-canonical generated artifact (`scripts/generate_skills_manifest.py` produces it, same file `AGENTS.md`'s manifest table and skill routing already trust).
- **Model choice:** delegate the script rewrite + new test to Antigravity CLI (Gemini 3.5 Flash Medium first, per item's suggested tier; GPT-OSS 120B as fallback) — small, well-bounded, single-file change. Claude Code orchestrates, reviews the diff, and runs tests itself per protocol (delegates bill the Google subscription, not Claude limits).
- **Skills routed:** `commit_and_changelog` (backlog/journal conventions), `test_and_verify` (test design standards).
- **Free tools:** none needed beyond what's already in the repo (`scripts/generate_skills_manifest.py` to refresh `.agents/skills.json` if stale).

## Plan

- [ ] Rewrite `scripts/library_statistics.py`: replace `count_files()` with `count_skills()` reading `.agents/skills.json`; update `badge_pattern` to match the current `Neural_Nodes` badge (`color=00ff41`); update `first_badge_line` fallback anchor to the current `SYS_CORE` badge line.
- [ ] Add `tests/test_library_statistics.py`: covers skill counting, in-place badge substitution when the pattern matches, fallback insertion when it doesn't, and idempotent re-run (no duplicate badge).
- [ ] Run the script live against the real repo to confirm it updates `README.md`'s badge to the true current skill count.
- [ ] Run `make test-changed` then full `make test`.
- [ ] File the broader dead-automation finding (this script silently no-op since the rebrand) as context in the Done note / changelog.
- [ ] Update improvements.md row 40 to Done, delete this journal, commit, push.

## Progress Log

- 2026-07-20 — Journal opened. Root cause traced to `scripts/library_statistics.py` / `update_badges.yml` mismatch with the post-rebrand README. Proceeding to delegate the fix.

## Next Step

Delegate the `scripts/library_statistics.py` rewrite + new test to Antigravity CLI, then review the diff and run tests.
