# Task Journal: Improvements item 28 — audit and dynamize the GitHub Actions workflows

## Summary

- **Task:** improvements.md #28 — audit all 9 workflows in `.github/workflows/`, delete the no-op `markdown_validation.yml`, gate publish workflows on green tests, restrict them to `v*` tags, add path filters so docs-only commits skip code CI, add concurrency groups everywhere, trim CodeQL's redundant push trigger, and stop `update_badges.yml`'s bot-commit from retriggering CI.
- **Status:** In progress
- **Started:** 2026-07-19
- **Agent and model:** Claude Code / Sonnet 5 (direct implementation, not delegated — see Model choice)

## Pre-Flight Re-Evaluation

- **Model choice:** Implementing directly rather than delegating. This item is a correctness-critical, tightly-coupled edit across 9 CI config files (reusable-workflow gating via `workflow_call`/`needs`, path filters, concurrency groups) where a subtle YAML mistake breaks every future push/release; the exact target content had to be fully designed up front regardless (same reasoning as the william_elias Feature 3 "write the spec myself" pattern), so writing it directly costs no more than writing an equivalent delegate brief, and avoids a round of diff-verification against a delegate for a change class (YAML control flow) that's easy to get subtly wrong.
- **Skills routed:** `devops` (CI/CD pipeline design — path filters, concurrency, workflow gating patterns).
- **Free tools:** `actionlint` (Go, MIT) — not installed; user approved `go install github.com/rhysd/actionlint/cmd/actionlint@latest` to validate the edited workflow YAML for syntax/semantic errors beyond what `pyyaml` catches. `pyyaml` (already installed) used for a basic parse check as a first pass.

## Plan

- [ ] Re-verify all 9 workflow files against the item's audit findings (done during selection — confirmed live)
- [ ] Delete `markdown_validation.yml`; remove its README.md "Security and Automation" bullet
- [ ] `test.yml`: add `paths-ignore` (docs/backlog-only skip) + `workflow_call:` trigger (so publish workflows can gate on it) + concurrency group
- [ ] `lint.yml`: add same `paths-ignore` + concurrency group
- [ ] `docker-publish.yml`: restrict to `v*.*.*` tags only (drop push-to-main), add `needs: test` via `uses: ./.github/workflows/test.yml`, add concurrency group
- [ ] `release_installer.yml`: restrict to `v*` tags only (drop push-to-main and the now-dead branch-snapshot step), add `needs: test`, add concurrency group
- [ ] `cross_platform.yml`: add `paths` filter (Go/installer files only), add concurrency group
- [ ] `codeql.yml`: drop redundant push-to-main trigger (keep PR + weekly schedule), add concurrency group
- [ ] `docs.yml`: add concurrency group only (item 27 owns docs-sync redesign)
- [ ] `update_badges.yml`: add `paths-ignore: README.md` + `[skip ci]` on its commit message, add concurrency group
- [ ] Install and run `actionlint` against all edited workflows; fix any findings
- [ ] `make test` full suite, update improvements.md row + Done note, delete journal, commit, push

## Progress Log

- 2026-07-19 — Journal opened. Re-verified live: 9 workflows present, `markdown_validation.yml` confirmed still a JSON no-op, `docker-publish.yml`/`release_installer.yml` confirmed triggering on every push to main, `update_badges.yml` confirmed committing to README.md with no paths-ignore/skip-ci. User approved installing `actionlint` for validation.

## Next Step

Install actionlint, then edit the 9 workflow files per the plan above.
