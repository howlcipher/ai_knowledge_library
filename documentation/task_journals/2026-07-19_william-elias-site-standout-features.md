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

- [ ] Feature 1: "View Source" badge next to the resume download link
- [ ] Feature 2: terminal-style hero intro animation (replaces/augments instant reveal)
- [ ] Feature 3: compact live-systems widget (GitHub API commit/CI status) with offline/rate-limit fallback
- [ ] Final pass: cross-check all three together for visual/contrast/clutter conflicts, update README if workflow changed, commit and push (confirm with user before push, since this repo deploys live on push to `main`)
- [ ] Delete this journal in the final commit

## Progress Log

- 2026-07-19 — Journal opened. Site reviewed: dark-mode-default, config-driven (`config.js`), existing a11y features (skip link, colorblind theme, focus states). Confirmed `agy` and local Ollama both available. Starting Feature 1.

## Next Step

Delegate Feature 1 (View Source badge) via `agy`, then verify diff and report back before starting Feature 2.
