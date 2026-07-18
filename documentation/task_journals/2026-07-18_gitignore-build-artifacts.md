# Task Journal: Ignore build artifacts and local state in git

## Summary

- **Task:** Improvement #2 — Ignore build artifacts and local state in git
- **Status:** Complete
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5

## Pre-Flight Re-Evaluation

- **Model choice:** Session is already running Claude Code on Fable 5; the task is trivial (gitignore + `git rm --cached`), well within Haiku 4.5's range, but switching models mid-session costs more than it saves. No API keys on this machine; no LLM pipeline runs needed for this task.
- **Skills routed:** `commit_and_changelog` (tier 1) — commit format `<type>(<scope>): <description>`, no dashes in subjects, secret scan before commit.
- **Free tools:** plain git (`git rm --cached`, `git check-ignore`) suffices; nothing to install.

## Plan

- [x] Add `.gitignore` rules: `.telemetry/`, `/build/`, `*.egg-info/` (installer and `__pycache__/` rules already exist from ce4309e, root-anchored — untouched)
- [x] `git rm --cached -r` the tracked artifacts: `.telemetry/telemetry.db`, `build/lib/**`, `installer`, all tracked `__pycache__` .pyc files, `src/ai_knowledge_library.egg-info/**`
- [x] Verify: `git status` clean of artifact noise, `git check-ignore -v` matches each path, `go build ./cmd/installer` and `pip install -e . --no-deps` both succeed and leave the tree clean
- [x] Update improvements.md (status, Done note, Completed entry), change_log.md + docs copy, commit, push

## Progress Log

- 2026-07-18 — Journal opened. Confirmed via `git ls-files`: telemetry.db, 27 build/lib files, installer binary, ~30 .pyc files, 5 egg-info files are tracked. Existing `.gitignore` already covers `/installer` and `__pycache__/` patterns; they were committed before the rules landed.
- 2026-07-18 — Added the three ignore rules, untracked all artifacts (`git rm --cached`). `git check-ignore -v` confirms every path matches a rule. Go installer rebuild and editable pip install both verified working with no new git noise.
- 2026-07-18 — Finding: eight one-off scratch files are also tracked at the repo root (`annotations.txt`, `coverage.out`, `logs.zip`, `parsed.txt`, `patch.diff`, `test_312_output.log`, `test_312_sudo.log`, `test_make.mk`), and the blanket `*.json` ignore hides `logs/payloads/**` pipeline evidence. Filed as new improvement #3; existing items renumbered 3→4 through 20→21 with cross-references updated.
- 2026-07-18 — improvements.md, change_log.md, and docs/change_log.md updated. Committed and pushed.

## Next Step

None — task complete. Next backlog item is #3 (purge tracked scratch files from the repo root).
