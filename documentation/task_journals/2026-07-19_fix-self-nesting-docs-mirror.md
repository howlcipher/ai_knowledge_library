# Task Journal: Fix the self-nesting docs site mirror (item 15)

Copy this file to `YYYY-MM-DD_<slug>.md` before starting a task (see the Working Protocol in `improvements.md`). Update and commit it at every milestone. A fresh session resumes by reading Status, the last Progress entry, and Next Step. When the task completes, move anything durable (findings, decisions, verification evidence) into the backlog Done note, the changelog, or a proper doc, then delete the journal in the task's final commit — only in-flight tasks have a journal here.

## Summary

- **Task:** improvements.md item 15 — Fix the self-nesting docs site mirror
- **Status:** In progress
- **Started:** 2026-07-19
- **Agent and model:** Claude Code (orchestrator) delegating implementation to Antigravity CLI / Gemini 3.5 Flash (Medium)

## Pre-Flight Re-Evaluation

- **Model choice:** Gemini 3.5 Flash (Medium) via `agy` headless — small Makefile edit plus one small test file; the backlog's "Gemini 3 Flash" no longer appears in `agy models`, Flash 3.5 is the live equivalent. Claude Code stays orchestrator per the delegation policy.
- **Skills routed:** `automation` (Makefile/workflow scripting standards), `commit_and_changelog` conventions for the close.
- **Free tools:** none needed beyond git, make, and the existing test suite.

## Findings so far (re-evaluation)

- The item's stated mechanism is outdated: current `Makefile` uses `cp -r documentation docs/` which **merges** on re-run (verified empirically) — it does not nest. The nesting came from the *old* recipe form `cp -r documentation docs/documentation` (commits `c97e3f2`, `7a6224a`), since removed.
- Residue is real: `docs/documentation/documentation/**` and `docs/.agents/.agents/**` hold 76 tracked files, redeployed to Pages on every CI run (`docs.yml` runs `make docs` on main and publishes `./docs`).
- Remaining defect in the current recipe: merge-without-delete strands stale files in every mirror dir (`docs/api`, `docs/documentation`, `docs/assets`, `docs/.agents`) when sources shrink or move — same staleness class item 4 fixed for the vector index.
- Fix shape: `rm -rf` the four mirror dirs at the top of the `docs` recipe, `git rm -r` the two committed nested trees, add a regression test (no nested mirror paths tracked; recipe cleans before copying).

## Plan

- [x] Re-evaluate item 15 against current code (mechanism corrected, residue confirmed)
- [ ] Delegate Makefile fix + regression test to Gemini 3.5 Flash via `agy`
- [ ] Review diff, `git rm -r` the committed nested trees myself
- [ ] Verify: `make docs` twice → identical tree, no nesting; tests green (`make test-changed`, `make test`)
- [ ] Close: Done note in improvements.md, changelog, delete journal, commit, push

## Progress Log

- 2026-07-19 — Selected item 15 (top open score 5.0). No stranded worktrees (`git worktree list` clean). Re-evaluation done: corrected the nesting mechanism (old `cp -r src docs/src` recipe form, not the current one), confirmed 76 tracked nested files and the CI deploy path. Journal committed before delegation.

## Next Step

Launch the `agy` delegation for the Makefile fix and regression test.
