# 🐛 Bug Backlog

This document is the authoritative, ranked backlog for known flaws, bugs, and broken items. It mirrors the structure of `improvements.md` and follows the same Working Protocol defined there: open a task journal, re-evaluate the model against what is currently available, route the crafted skills, scan for free tools, then fix, verify, commit, and push. Bugs are prioritized independently of new features and generally outrank improvement work of similar effort.

## Ranked Backlog (best ROI first)

Pending bugs carry the same diminishing-returns score defined in `improvements.md` (Score = Value × Decay ÷ Effort, ROI floor 0.5, recomputed at every groom). Bugs rarely decay — a defect's cost does not shrink because other defects were fixed — so Decay is normally 1.0, and bugs still outrank improvement work of similar score. A bug below the floor stays open, flagged ⚠️, and needs explicit user confirmation before being worked. When a new bug is found, add a row here and a matching detail section below, then work the table top down.

| # | Bug | Status | Score (V×D÷E) | Claude model | Gemini model | ROI rationale |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [Remove the obfuscated dead hook installer](#1-remove-the-obfuscated-dead-hook-installer) | Done (2026-07-19) | — | Haiku 4.5 | Gemini 3 Flash | Minutes of work; deletes deliberately lint-evading dead code before an agent trusts or reruns it |
| 2 | [De-obfuscate the pre-push hook filename](#2-de-obfuscate-the-pre-push-hook-filename) | Pending | 5.0 = 5×1.0÷1 | Haiku 4.5 | Gemini 3 Flash | Seconds of work; removes the exact obfuscation pattern that got bug 1 deleted, in a script the installer now runs automatically (improvements item 13) |

## Details

### 1. Remove the obfuscated dead hook installer
Found during the 2026-07-18 backlog groom.
**Done 2026-07-19 (commit 89b2bb2):** `scripts/install_git_hooks.py` deleted. Claims re-verified live before deletion: the only references were this backlog and `improvements.md` themselves, and `.git/hooks/` contained only the maintained `pre-commit` hook. No replacement needed; a post-commit Chroma sync, if ever wanted, goes plainly into the maintained installers (see improvements item 13). `scripts/install_git_hooks.py` builds the hook name `post-commit` from a chain of `chr()` calls with the comment "Bypassing strict formatting rules dynamically" — deliberate obfuscation to evade the repo's formatting checks. The script is dead: nothing references it (not the Makefile, `scripts/bootstrap.py`, CI, or any doc), the post-commit hook it would install is not present in `.git/hooks/` on this machine, and it predates the current hook installers (`install_pre_commit_hook.py`, `install_pre_push_hook.py`), which cover the real hook needs. Its payload (run `scripts/sync_context.py` after every commit) is also questionable — a full ChromaDB sync per commit — and `make` already exposes `sync_context.py` directly. Fix: delete `scripts/install_git_hooks.py`; if a post-commit Chroma sync is ever wanted, reimplement it plainly inside the maintained installer scripts. Coordinates with improvements item 13 (wiring hook installation into bootstrap), which should route through the maintained installers only.

### 2. De-obfuscate the pre-push hook filename
Found during improvements item 13 (2026-07-19). `scripts/install_pre_push_hook.py` builds the hook filename `"pre-push"` via a chain of eight `chr()` calls instead of a plain string literal — the identical pattern that got `scripts/install_git_hooks.py` deleted as bug 1 ("deliberate obfuscation to evade the repo's formatting checks"). Unlike bug 1, this script is not dead: it is one of the two maintained hook installers, and improvements item 13 just wired it into `cmd/installer`'s automatic `Install()` flow, so it now runs on every machine that installs this library. Fix: replace the `chr()` chain with the literal string `"pre-push"`. No behavior change; trivial diff.

## ✅ Resolved

- **Bug 1 — Remove the obfuscated dead hook installer (fixed 2026-07-19, commit 89b2bb2):** deleted `scripts/install_git_hooks.py`, an unreferenced installer that assembled the hook name `post-commit` from `chr()` calls to evade formatting checks. The maintained installers cover all real hook needs.
- All issues tracked before 2026-07-18 were resolved prior to this restructure. Resolved bugs move here with their fix date and commit hash; the fix itself is also recorded in `change_log.md`.
