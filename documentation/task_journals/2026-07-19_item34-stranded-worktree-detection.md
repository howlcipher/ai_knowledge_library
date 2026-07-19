# Task Journal: Item 34 — Detect stranded worktree branches during item selection

Copy of TEMPLATE.md per the Working Protocol in `improvements.md`.

## Summary

- **Task:** improvements.md #34 — extend the Select step in `.agents/prompts/work_next_item.md` (and `resume_task.md`) to check `git worktree list` and unmerged `worktree-*` branches for in-flight work, treat an uncommitted journal inside a worktree as a resume point, and require finished worktree branches to be merged and removed before a session ends.
- **Status:** In progress
- **Started:** 2026-07-19
- **Agent and model:** Claude Code (Fable 5) orchestrating; implementation delegated per policy

## Pre-Flight Re-Evaluation

- **Model choice:** Item column suggests Gemini 3 Flash via agy headless. Will check `agy models` live; this is a prose-only edit to two prompt files, so the cheapest available delegate suffices. Fallback: apply directly (fully-specified edit) if Antigravity quota is exhausted.
- **Skills routed:** `technical_writing` (doc standards), `hallucination_guardrails` (tier 0, always on). No code skills needed — markdown-only change.
- **Free tools:** none beyond git/agy; no installs needed.

## Plan

- [x] Verify no stranded worktrees exist right now (`git worktree list` clean, no worktree-* branches)
- [ ] Delegate the prompt edits (work_next_item.md Select step + resume_task.md step 1) to a non-Claude model
- [ ] Review diff, run `make test-changed` then `make test`
- [ ] Mark #34 Done in improvements.md, delete this journal, commit, push

## Progress Log

- 2026-07-19 — Item re-evaluated: still valid. The prompt files are unchanged since the item was filed; `work_next_item.md` step 1 only checks `documentation/task_journals/`, and `resume_task.md` step 1 only lists the same directory. No live worktrees exist today, so the edit is purely preventive, exactly as filed.

## Next Step

Delegate the two-file prompt edit via agy (Gemini 3 Flash), or apply directly if quota is dead.
