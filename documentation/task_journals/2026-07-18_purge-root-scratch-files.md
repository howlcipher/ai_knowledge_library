# Task Journal: Purge tracked scratch files from the repo root

## Summary

- **Task:** Improvement #3 — Purge tracked scratch files from the repo root
- **Status:** In progress
- **Started:** 2026-07-18
- **Agent and model:** Claude Code / Fable 5

## Pre-Flight Re-Evaluation

- **Model choice:** Session is already running Claude Code on Fable 5; the task is trivial (per-file triage + `git rm` + ignore rules), within Haiku 4.5's range, but a mid-session model switch costs more than it saves. No LLM pipeline runs needed.
- **Skills routed:** `commit_and_changelog` (tier 1) — commit format `<type>(<scope>): <description>`, no dashes in subjects, secret/PII scan of staged changes before commit.
- **Free tools:** plain git (`git rm`, `git check-ignore`, `git log --follow`) plus `unzip -l` for the archive check; nothing to install.

## Triage (per-file verdicts)

| File | Content | Verdict |
| --- | --- | --- |
| `annotations.txt` | CI failure log snippet (anyio cancel-scope traceback, Node 20 deprecation) from a July 11 debugging session | Scratch — delete |
| `coverage.out` | Generated Go coverage profile; ignore rule already exists (`coverage.out`), tracked before it landed | Generated — delete + untrack |
| `logs.zip` | 180 bytes, not even a valid zip (`unzip -l` fails: no central directory) | Corrupt scratch — delete |
| `parsed.txt` | One-off CI job status dump (`test-python: in_progress`, ...) | Scratch — delete |
| `patch.diff` | Patch for commit `07d2146` "fix: resolve test failures and go spinner compilation bug" — already merged on main | Scratch — delete |
| `test_312_output.log` | One line: docker socket permission error | Scratch — delete |
| `test_312_sudo.log` | Empty file | Scratch — delete |
| `test_make.mk` | Two-line `exit 1` throwaway makefile | Scratch — delete |

Nothing qualifies as evidence worth relocating: the CI failures these files came from are fixed in history, and the patch is merged.

## Plan

- [x] Triage each of the 8 files (evidence vs scratch) — all scratch, see table
- [x] `git rm` all 8 (removes from index and disk; coverage.out regenerates via `go test -coverprofile`)
- [x] Add root-anchored ignore rules for the recurring patterns: `/*.log`, `/*.diff`, `/*.zip` (skip name rules for one-off txt/mk scratch that will not recur)
- [x] Decide the `*.json` / `logs/payloads/**` question: keep ignored (see decision below)
- [x] Verify: `git status` clean, `git check-ignore -v` matches the new patterns, no tracked file elsewhere is hidden by the new rules
- [x] Update improvements.md (status, Done note, Completed entry), change_log.md + docs copy, commit, push

## Decision: `*.json` blanket ignore vs `logs/payloads/**`

Keep `logs/payloads/**` ignored. The payload dirs are per-run pipeline state (full LLM outputs, one dir per task id) that churns on every run; committing them would bloat history and risk committing model output nobody reviewed. The durable conclusions from failed runs already land in `issues.md`, `improvements.md` (items 5–12 all came from those runs), and task journals. Revisit only if a future post-mortem actually needs a payload that was lost.

## Progress Log

- 2026-07-18 — Journal opened. Confirmed all 8 files tracked via `git ls-files`; triaged contents (table above). patch.diff commit verified merged (`git branch --contains 07d2146` → main). `logs/` has no tracked files, so the new root-anchored rules hide nothing.
- 2026-07-18 — Removed the 8 files (`git rm`), added `/*.log`, `/*.diff`, `/*.zip` root-anchored rules with a comment. Verified `git check-ignore -v` matches probe names at root and does NOT match nested paths (`logs/x.log` unmatched, as intended, though logs/ has no tracked files anyway). `git status` clean after commit.
- 2026-07-18 — improvements.md (#3 Done + note + Completed entry), change_log.md and docs/change_log.md updated. Committed and pushed.

## Next Step

None — task complete. Next backlog item is #4 (make vector index rebuilds idempotent).
