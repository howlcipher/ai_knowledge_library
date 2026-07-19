# 🐛 Bug Backlog

This document is the authoritative, ranked backlog for known flaws, bugs, and broken items. It mirrors the structure of `improvements.md` and follows the same Working Protocol defined there: open a task journal, re-evaluate the model against what is currently available, route the crafted skills, scan for free tools, then fix, verify, commit, and push. Bugs are prioritized independently of new features and generally outrank improvement work of similar effort.

## Ranked Backlog (best ROI first)

Rank weighs user impact and blast radius against fix effort. When a new bug is found, add a row here and a matching detail section below, then work the table top down.

| # | Bug | Status | Claude model | Gemini model | ROI rationale |
| --- | --- | --- | --- | --- | --- |
| 1 | [Remove the obfuscated dead hook installer](#1-remove-the-obfuscated-dead-hook-installer) | Pending | Haiku 4.5 | Gemini 3 Flash | Minutes of work; deletes deliberately lint-evading dead code before an agent trusts or reruns it |

## Details

### 1. Remove the obfuscated dead hook installer
Found during the 2026-07-18 backlog groom. `scripts/install_git_hooks.py` builds the hook name `post-commit` from a chain of `chr()` calls with the comment "Bypassing strict formatting rules dynamically" — deliberate obfuscation to evade the repo's formatting checks. The script is dead: nothing references it (not the Makefile, `scripts/bootstrap.py`, CI, or any doc), the post-commit hook it would install is not present in `.git/hooks/` on this machine, and it predates the current hook installers (`install_pre_commit_hook.py`, `install_pre_push_hook.py`), which cover the real hook needs. Its payload (run `scripts/sync_context.py` after every commit) is also questionable — a full ChromaDB sync per commit — and `make` already exposes `sync_context.py` directly. Fix: delete `scripts/install_git_hooks.py`; if a post-commit Chroma sync is ever wanted, reimplement it plainly inside the maintained installer scripts. Coordinates with improvements item 13 (wiring hook installation into bootstrap), which should route through the maintained installers only.

## ✅ Resolved

- All issues tracked before 2026-07-18 were resolved prior to this restructure. Resolved bugs move here with their fix date and commit hash; the fix itself is also recorded in `change_log.md`.
