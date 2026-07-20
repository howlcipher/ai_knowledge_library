# Task Journal: Claude Code backend for pipeline tiers

## Summary

- **Task:** improvements.md item 20 — Claude Code backend for pipeline tiers. Add a `claude_code` option to `payload_pipeline.tier_models` that shells out to headless `claude -p ... --output-format json` instead of routing through LiteLLM, so a tier can be judged by the Claude Pro subscription.
- **Status:** In progress
- **Started:** 2026-07-20
- **Agent and model:** Claude Code / Sonnet 5 (orchestrator), delegating implementation to Antigravity CLI

## Pre-Flight Re-Evaluation

- **Model choice:** `agy` (Antigravity CLI) is live this session (`agy models` succeeded after an initial spurious classifier denial when bundled with unrelated commands in one Bash call — isolating the call fixed it). Local Ollama server is NOT running this session (`curl localhost:11434/api/tags` → connection refused, exit 7) — not a delegation option today. Picked Gemini 3.1 Pro (High) via agy for the implementation pass: this touches `orchestrator.py`'s tier-agent construction and needs correctness, matching the item's "Gemini 3 Pro" column; will escalate to Antigravity's Claude Sonnet 4.6 (Thinking) if Gemini 3.1 Pro's diff has defects, since that bills the Google subscription, not this session's Claude limits.
- **Skills routed:** `software_development` (least-privilege subprocess execution, explicit timeouts, defensive error handling — all baked into the design below).
- **Free tools:** none new; reusing existing patterns (`transport_retry.py`'s generic-exception contract, `Agent`'s `generate_response` interface).
- **Environment note (found this session):** invoking `claude` directly from this sandboxed Bash tool is blocked by the Claude Code auto-mode classifier ("Blocked by classifier"), even `claude --version`. This means the new `ClaudeCodeAgent` backend cannot be live-exercised from inside this orchestrating session — verification is mocked-subprocess only, same constraint pattern as item 32's un-verifiable-live web_research path. A future session running outside this sandbox restriction (or the user running it manually) would be needed for a real live check.

## Plan

- [ ] New `src/core/claude_code_backend.py`: `ClaudeCodeAgent` class matching `Agent`'s `generate_response(user_prompt, context="", raise_errors=False) -> object with .content` contract, backed by `subprocess.run(["claude", "-p", ...], timeout=..., capture_output=True)` + `--output-format json` parsing (`result`/`is_error` keys). `CLAUDE_CODE_MODEL = "claude_code"` sentinel constant.
- [ ] `src/core/orchestrator.py`: extract tier-agent construction into a module-level `build_tier_agent(name, prompt, model, timeout=None, response_format=None)` so it's unit-testable; branches to `ClaudeCodeAgent` when `model == CLAUDE_CODE_MODEL`, else the existing `Agent`. Wire `run_payload_loop`'s `tier_agent` closure to call it.
- [ ] `src/core/provider_preflight.py`: special-case `CLAUDE_CODE_MODEL` in `preflight_models`/`_check_generation` to check `shutil.which("claude")` instead of a litellm generation ping (litellm has no `claude_code` provider).
- [ ] `config/settings.yaml`: add `claude_code` as a documented example value in the `tier_models` comments.
- [ ] `documentation/multi_agent_payload_protocol.md`: document the new backend option.
- [ ] Tests: `tests/test_claude_code_backend.py` (mocked `subprocess.run` — success, `is_error` true, non-zero exit, malformed JSON, timeout, `FileNotFoundError`), plus additions to `tests/test_orchestrator.py` (`build_tier_agent` dispatches to `ClaudeCodeAgent` vs `Agent`) and `tests/test_provider_preflight.py` (`claude_code` model checked via `shutil.which`, not litellm).
- [ ] Delegate to agy, review diff + tests against this plan, run `make test-changed` then `make test`.
- [ ] Update improvements.md row 20 to Done, delete this journal, commit, push.

## Progress Log

- 2026-07-20 10:xx — Selected item 20 (tied top score 1.0 with items 38/40; table order tiebreak). Re-verified live: `orchestrator.py`'s `tier_agent` still only ever builds a LiteLLM `Agent`, no `claude_code` branch exists — item still fully open as filed. Read `Agent`/`tier_agent`/`call_fn` contract in `orchestrator.py` and `call_with_transport_retry`'s generic-exception retry contract in `transport_retry.py` to design a drop-in-compatible `ClaudeCodeAgent`. Housekeeping: deleted stale untracked `.agents/commands/` + `.claude/commands` symlink left over from the previous session's commit (superseded by `.agents/skill_commands/` + `.claude/skills/` per that commit's own message).

## Next Step

Write and send the delegation brief to agy (Gemini 3.1 Pro, High) for the plan above, then review the diff.
