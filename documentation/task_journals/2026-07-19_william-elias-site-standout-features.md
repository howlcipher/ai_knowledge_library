# Task Journal: william_elias resume site — standout visual/technical features

## Summary

- **Task:** Not a backlog item — ad hoc request in a sibling repo (`/home/howlcipher/dev/william_elias`, public GitHub Pages resume site). Add three features, one at a time, in priority order: (1) "View Source" badge next to the resume download, (2) terminal-style hero intro animation, (3) a compact "live systems" widget (GitHub API: latest commit/CI status) with a graceful offline/rate-limit fallback.
- **Status:** In progress
- **Started:** 2026-07-19
- **Agent and model:** Claude Code / Sonnet 5 (orchestrator) delegating implementation to Antigravity CLI (`agy`)

## Pre-Flight Re-Evaluation

- **Model choice:** Delegate implementation via `agy` per [[delegate-to-save-claude-limits]] to preserve Claude Pro limits. Start with Gemini 3.5 Flash (Medium) (cheapest capable per `agy models`); escalate to Gemini 3.1 Pro or Claude Sonnet 4.6 (via Google billing) if quality/precision is insufficient for public-facing content. Fall back to local Ollama `qwen3:30b-instruct` if Gemini quota is exhausted (per [[agy-gemini-quota-shared]]).
- **Skills routed:** `accessibility` (contrast, semantic HTML, keyboard nav, ARIA for the new widget/animation), `visual_design` (hierarchy, whitespace, don't let the widget outweigh the resume content), `color_theory` (if new colors are needed, must fit existing dark/light/colorblind token system in `style.css`), `frontend_engineering` (mostly React/TS-focused, not directly applicable to this vanilla JS static site — used only its general modularity/separation-of-concerns guidance).
- **Free tools:** No new installs anticipated — plain HTML/CSS/JS, GitHub's public REST API (unauthenticated, rate-limited) for the widget. **Known constraint:** headless Firefox (flatpak) fails in this sandbox (`CanCreateUserNamespace() clone() failure: EPERM`), and no other headless-render tool is installed — visual verification of each change must be done by other means (manual code review, syntax checks, possibly asking the user to eyeball it) and reported honestly if it can't be confirmed live.
- **Verification discipline:** Per [[agy-delegate-can-fake-success]], always run `git status`/`git diff` after every `agy` delegation before trusting its own summary — never commit on the delegate's word alone.

## Plan

- [x] Feature 1: "View Source" badge next to the resume download link
- [x] Feature 2: terminal-style hero intro animation (replaces/augments instant reveal)
- [x] Feature 3: compact live-systems widget (GitHub API commit/CI status) with offline/rate-limit fallback — scoped down to a commit widget, not CI, since the repo has no Actions workflow
- [x] Final pass: cross-check all three together for visual/contrast/clutter conflicts, update README, commit — awaiting user confirmation to push (live-deploy repo)
- [ ] Delete this journal in the final commit (after push confirmation)

## Progress Log

- 2026-07-19 — Journal opened. Site reviewed: dark-mode-default, config-driven (`config.js`), existing a11y features (skip link, colorblind theme, focus states). Confirmed `agy` and local Ollama both available. Starting Feature 1.
- 2026-07-19 — Gemini tiers all quota-exhausted account-wide (18h46m reset), confirming [[agy-gemini-quota-shared]] still holds. Fell back to GPT-OSS 120B (Medium) via `agy`, independent quota, worked both times.
- 2026-07-19 — Feature 1 delegated to GPT-OSS 120B: added `personal.sourceRepo` to `config.js` and a matching "View Source" contact-pill in `script.js`. Verified via `git diff` (not the delegate's own summary, per [[agy-delegate-can-fake-success]]) — edits were real and exactly as specified. Committed `4634365`.
- 2026-07-19 — Feature 2 delegated to GPT-OSS 120B: CSS-only typewriter reveal on the hero tagline (`.tagline.terminal-type`), `terminal-typing`/`terminal-caret` keyframes, mobile-breakpoint fallback. Verified via `git diff` — matched brief exactly. **Caught a bug in my own brief during review, not the delegate's fault**: animating `width: 0 → 100%` resolves against the *containing block*, not the text's shrink-to-fit width, so the cursor would land in empty space past the (shorter) tagline text instead of at its end. Fixed directly by animating `max-width` instead of `width` (relies on `display: inline-block` + `overflow: hidden` capping the rendered width at the text's intrinsic size once max-width exceeds it). Could not visually confirm in a browser — headless Firefox (flatpak) fails in this sandbox (`CanCreateUserNamespace() clone() failure: EPERM`) and no other renderer is installed; verified by CSS layout reasoning only, told the user this explicitly. Committed `ebf8e76`.

- 2026-07-19 — Feature 3 designed directly (not delegated blind): checked the repo has no `.github/workflows`, so scoped down from "CI status" to a "last synced" widget (latest commit via GitHub API, relative time + short SHA, localStorage cache with 10 min TTL, silent fallback to stale cache or nothing on fetch failure — never shows an error state). Wrote the exact HTML/CSS/JS myself, then had GPT-OSS 120B insert it verbatim via `agy` so the diff would be easy to verify against a known-correct spec. **Delegate only completed part of the brief**: it wired the `initLastSynced()` call site into `script.js` but silently dropped the three function definitions it was told to append — caught immediately via `git diff` (per [[agy-delegate-can-fake-success]], this is exactly the failure mode that check exists for, just partial instead of total this time). Added the missing functions directly since they were already fully specified. No JS runtime available in this sandbox (no `node`/`deno`/`bun`, no `esprima`) to syntax-check, so verified by full manual read-through instead — reasoned through brace/paren balance, function hoisting (call site precedes declaration, which is safe for `function` declarations), and confirmed the GitHub API response shape (`sha`, `commit.author.date`, `html_url`) matches what the code reads. Committed `c513dcd`.
- 2026-07-19 — Cross-checked all three features together: they occupy three separate visual zones (hero pills, hero tagline, footer), no clutter/contrast conflicts found. Documented all three in README (`76a2e05`). Noted but did not fix (out of scope, pre-existing, affects other links too): none of the site's `target="_blank"` links set `rel="noopener noreferrer"` — flagged to the user as an optional follow-up rather than silently rewriting unrelated existing links.
- 2026-07-19 — Could not visually verify any of the three features in a real browser at any point in this task: headless Firefox (flatpak) fails in this sandbox with `CanCreateUserNamespace() clone() failure: EPERM`, and no other renderer (wkhtmltopdf, weasyprint, chromium) is installed. All verification was via `git diff` against a fully-specified spec plus manual code/CSS-layout reasoning. Told the user this explicitly rather than claiming a visual check that didn't happen.

## Next Step

All three features implemented, verified, and committed locally in `william_elias` (not yet pushed — this repo deploys live on push to `main`, holding for explicit user confirmation). Once the user confirms: push, then delete this journal in that same commit.
