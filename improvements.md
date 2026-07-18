# 🚀 Improvement Backlog

This document is the authoritative, ranked backlog for the AI Knowledge Library. It is designed so a fresh session (Claude Code or Gemini CLI) can pick up the next item with zero prior chat context.

## Working Protocol

This protocol applies to every worked task — backlog improvements and bug fixes alike. Bugs are tracked in `issues.md`, which mirrors this file's format and shares this protocol; a hotfix without a backlog row still gets steps 1 through 4 and 7.

1. **Open a task journal.** Copy `documentation/task_journals/TEMPLATE.md` to `documentation/task_journals/YYYY-MM-DD_<slug>.md`. The journal is the resume point after a session limit or power outage: update it and commit at every milestone, and always keep its "Next step" line current so a fresh session can continue from the journal alone.
2. **Re-evaluate the model (every run, before starting).** The table's model columns are starting suggestions, not commitments. Check what is actually available right now — currently: Claude Pro subscription (Claude Code), Gemini Pro subscription (Gemini CLI), and local Ollama (`curl localhost:11434/api/tags` — models change). Update this sentence if subscriptions change. Pick the least expensive available model that can do the job well and escalate only if the task proves harder than expected; in Claude Code switch with `/model` or delegate to a subagent with the chosen model, in Gemini CLI launch with `gemini -m <model>`. Record the choice and one line of reasoning in the journal.
3. **Route the crafted skills.** Check the skills manifest (`.agents/skills.json` or the AGENTS.md table) for skills matching the task and read the matching SKILL.md files before planning. Honor tier precedence and the Related Skills deferrals.
4. **Scan for helpful free tools.** Briefly consider whether a free or open source tool (a CLI already installed, a linter, a library, an MCP server) would materially improve the work. Record recommendations in the journal; use tools that are already available freely, and ask before installing anything new.
5. **Read the detail section** for the item (linked from the table) plus any referenced docs before coding. Background docs: `documentation/multi_agent_payload_protocol.md` and ADR 0003.
6. **Constraints:** this machine has no Anthropic or Gemini API keys; live LLM pipeline runs go through local Ollama.
7. **Finish the loop:** verify the change works, commit with `<type>(<scope>): <description>`, set the item's Status to `Done (YYYY-MM-DD)` in the table, mark the journal complete, and push.

## Ranked Backlog (best ROI first)

Rank weighs impact against effort: quick unblocking fixes first, large architecture efforts last.

| # | Improvement | Status | Claude model | Gemini model | ROI rationale |
| --- | --- | --- | --- | --- | --- |
| 1 | [Rebuild the vector index](#1-rebuild-the-vector-index) | Done (2026-07-18) | Haiku 4.5 | Gemini 3 Flash | Minutes of work; unblocks semantic search over the newly refined skills |
| 2 | [Ignore build artifacts and local state in git](#2-ignore-build-artifacts-and-local-state-in-git) | Done (2026-07-18) | Haiku 4.5 | Gemini 3 Flash | Minutes of work; clears permanent noise from git status and prevents accidental commits |
| 3 | [Purge tracked scratch files from the repo root](#3-purge-tracked-scratch-files-from-the-repo-root) | Pending | Haiku 4.5 | Gemini 3 Flash | Minutes of work; stops one-off scratch files traveling with every clone |
| 4 | [Make vector index rebuilds idempotent](#4-make-vector-index-rebuilds-idempotent) | Pending | Haiku 4.5 | Gemini 3 Flash | Minutes of work; prevents stale chunks from silently corrupting every future rebuild |
| 5 | [Preflight the provider before a run](#5-preflight-the-provider-before-a-run) | Pending | Sonnet 5 | Gemini 3 Flash | Small change; stops entire runs being wasted on a dead server or missing model tag |
| 6 | [Per tier LLM timeout](#6-per-tier-llm-timeout) | Pending | Haiku 4.5 | Gemini 3 Flash | Config plumbing only; removes a known hard failure for 30B local models |
| 7 | [Separate transport failures from validation failures](#7-separate-transport-failures-from-validation-failures) | Pending | Sonnet 5 | Gemini 3 Pro | Medium effort; makes every future failure diagnosable instead of masked |
| 8 | [Provider enforced structured outputs](#8-provider-enforced-structured-outputs) | Pending | Sonnet 5 | Gemini 3 Pro | Medium effort; biggest single reliability win for small local models |
| 9 | [Show exact object shapes in tier prompts](#9-show-exact-object-shapes-in-tier-prompts) | Pending | Sonnet 5 | Gemini 3 Flash | Small prompt change; directly cuts the observed schema misses, complements #8 |
| 10 | [Persist all attempt errors](#10-persist-all-attempt-errors) | Pending | Haiku 4.5 | Gemini 3 Flash | Small change; preserves post mortem evidence currently thrown away |
| 11 | [Guard against oversized local models](#11-guard-against-oversized-local-models) | Pending | Sonnet 5 | Gemini 3 Flash | Small change; makes OOM/crash loops diagnosable from the log |
| 12 | [Emit gate failures into telemetry](#12-emit-gate-failures-into-telemetry) | Pending | Haiku 4.5 | Gemini 3 Flash | Small change; starts tracking schema failure rate per model |
| 13 | [Install the pre-commit hook via bootstrap](#13-install-the-pre-commit-hook-via-bootstrap) | Pending | Haiku 4.5 | Gemini 3 Flash | Small change; removes a silent per machine setup gap |
| 14 | [Sync the docs site changelog automatically](#14-sync-the-docs-site-changelog-automatically) | Pending | Haiku 4.5 | Gemini 3 Flash | Two line hook addition; stops docs/change_log.md drifting from the real changelog |
| 15 | [Fix the self-nesting docs site mirror](#15-fix-the-self-nesting-docs-site-mirror) | Pending | Haiku 4.5 | Gemini 3 Flash | Small Makefile fix; stops the Pages mirror doubling itself on every `make docs` re-run |
| 16 | [`pipeline_pass` frontmatter and dispatcher](#16-pipeline_pass-frontmatter-and-dispatcher) | Pending | Sonnet 5 | Gemini 3 Pro | Medium effort; routes reviewer skills into the right pipeline pass |
| 17 | [Claude Code backend for pipeline tiers](#17-claude-code-backend-for-pipeline-tiers) | Pending | Sonnet 5 | Gemini 3 Pro | Medium effort; adds a strong subscription backed judge for Tier 1 |
| 18 | [Calibrate the skill router score threshold](#18-calibrate-the-skill-router-score-threshold) | Pending | Fable 5 | Gemini 3 Pro | Needs judgment (labeled prompt set + eval design), modest payoff beyond triggers |
| 19 | [OpenTelemetry integration](#19-opentelemetry-integration) | Pending | Sonnet 5 | Gemini 3 Pro | Larger effort; better observability but no current outage it would have caught |
| 20 | [Homelab MCP server](#20-homelab-mcp-server) | Pending | Fable 5 | Gemini 3 Pro | High long term value but a full architecture evaluation and build |
| 21 | [Automated job hunting pipeline](#21-automated-job-hunting-pipeline) | Pending | Fable 5 | Gemini 3 Pro | High personal value but the largest, most open ended build |

## Details

### 1. Rebuild the vector index
`build_vector_index.py` was fixed to include dot directories (`.agents/skills/**` was invisible to the old glob), but the index has not been rebuilt since. The full skill refinement of 2026-07-18 (tiers, triggers, deduplicated content, Related Skills sections) is therefore invisible to semantic search. Run the rebuild so semantic search retrieves the refined skill content, and spot check a few queries (e.g. a security prompt should surface `cyber_security`).

**Done 2026-07-18:** Index rebuilt (219 chunks) with the `docs/` Pages mirror pruned from the scan — the first build indexed the mirror too (410 chunks) because the mirror paths contain the `.agents`/`documentation` substrings the file filter keeps, and duplicate copies crowded out results. Spot checks pass: security → `cyber_security`, crash triage → `defensive_debugging`, Terraform/K8s → `devops_sre`, resume → `career_assistant`. Findings spawned items 4 and 15. Journal: `documentation/task_journals/2026-07-18_rebuild-vector-index.md`.

### 2. Ignore build artifacts and local state in git
Several generated or local-state files are tracked or untracked-dirty and permanently clutter `git status`: `.telemetry/telemetry.db`, `build/lib/**`, `src/ai_knowledge_library.egg-info/**`, `__pycache__/` (including `scripts/__pycache__`), and the compiled Go binary `installer` (ELF executable rebuilt locally; track its source, not the binary). Add `.gitignore` entries, `git rm --cached` the already-tracked ones, and verify a fresh clone plus build still works. Check the existing installer-related `.gitignore` anchoring from commit `ce4309e` so the rules do not conflict.

**Done 2026-07-18:** Added `/build/`, `*.egg-info/`, and `.telemetry/` rules (installer and `__pycache__/` rules already existed from `ce4309e`; those files were simply committed before the rules landed) and untracked 60+ artifact files. Verified every path now matches an ignore rule via `git check-ignore -v`, and that the artifacts regenerate from source: `go build ./cmd/installer` and `pip install -e .` both succeed and leave `git status` clean. Findings spawned item 3 (tracked scratch files). Journal: `documentation/task_journals/2026-07-18_gitignore-build-artifacts.md`.

### 3. Purge tracked scratch files from the repo root
One-off working files are committed at the repo root and travel with every clone: `annotations.txt`, `coverage.out` (tracked before its ignore rule landed), `logs.zip`, `parsed.txt`, `patch.diff`, `test_312_output.log`, `test_312_sudo.log`, and `test_make.mk`. Decide per file whether it is evidence worth keeping (relocate under `documentation/` or `logs/`) or scratch (delete and `git rm`), then untrack the scratch set and add ignore rules for the recurring patterns (`*.log`, `*.diff`, `*.zip` at root, or specific names). Found during item 2, which fixed the generated-artifact half of the same problem. Related observation: the blanket `*.json` ignore rule silently hides `logs/payloads/**` pipeline run evidence from git; decide deliberately whether that should stay ignored or get a negation rule.

### 4. Make vector index rebuilds idempotent
`build_vector_index.py` only upserts; it never deletes existing chunks. Chunk ids are `<path>_<n>`, so when a file shrinks, moves, or is deleted, its leftover ids stay in the collection and every rebuild after content changes strands stale chunks (the 2026-07-18 rebuild required a manual `rm -rf .chroma` to purge the mirror duplicates). Drop and recreate the collection at the start of the build (or delete ids absent from the new scan) so a plain rerun always yields a clean index. Apply the same fix to the pgvector backend path.

### 5. Preflight the provider before a run
Run 1 (2026-07-17) spent all three validation attempts against a crashed Ollama server, and run 2 against a model tag that had been removed mid session. A cheap ping before pass 1 (list models, verify the configured tag exists, one token generation) would fail fast with an actionable error.

### 6. Per tier LLM timeout
The 30B model timed out at LiteLLM's default 600s while generating the full payload envelope. Add a `timeout` setting to `payload_pipeline` (or per entry in `tier_models`) and pass it through `litellm.completion`.

### 7. Separate transport failures from validation failures
`litellm.APIConnectionError` (server crash, model not found, timeout) surfaces as an empty response, which the gate scores as a `parse` failure and burns one of the three validation attempts. The persisted failed payload then reports `failure_vector: validation_gate.parse`, masking the real cause. Catch provider exceptions in the tier call path, retry them with backoff without consuming a validation attempt, and record a distinct error code (e.g. `UPSTREAM_UNAVAILABLE`) with the provider message in `error.context`.

### 8. Provider enforced structured outputs
`qwen3:30b-instruct` produced parseable JSON but invented fields on both real attempts (`lineage.history[0].action/details/timestamp`, then `critique.findings[0].description`). The VALIDATION ERROR feedback loop measurably improved attempt 2, but prompt discipline alone is weak on small local models. Ollama and LiteLLM support `response_format` with a JSON schema; passing `agent_task_payload.schema.json` (or a per pass subset) would make schema compliance mechanical instead of behavioral.

### 9. Show exact object shapes in tier prompts
The invented `lineage.history` fields suggest the model never saw the required entry shape. Embed a one line example of each nested object (history entry, finding, adversarial test) in the tier prompts, or echo the relevant schema fragment inside the VALIDATION ERROR feedback.

### 10. Persist all attempt errors
The failed payload keeps only the final attempt's errors, so the schema violations from attempts 1 and 2 of run 3 are lost. Append a per attempt error history to `error.context` for post mortems.

### 11. Guard against oversized local models
`qwen3:30b-a3b` crashed the Ollama server mid load (29GB RAM host). When the configured model is served by a local endpoint, surface the provider's error body (Ollama returns JSON error messages) instead of the generic connection error, so OOM/crash loops are diagnosable from the pipeline log.

### 12. Emit gate failures into telemetry
The validation gate prints failures but does not log them through `telemetry_logger`, so schema failure rate per model is not yet a tracked metric (recommended in `documentation/multi_agent_payload_protocol.md`).

### 13. Install the pre-commit hook via bootstrap
`.git/hooks` is not versioned; each machine needs a one time `python scripts/install_pre_commit_hook.py` (which now includes the skills manifest/index regeneration and the fixed `.env` guard). Wire it into `scripts/bootstrap.py` or the installer so it happens automatically.

### 14. Sync the docs site changelog automatically
`docs/change_log.md` is a manual byte-for-byte copy of `change_log.md` for the GitHub Pages site and will drift as soon as someone updates the changelog without remembering the copy. Extend the pre-commit hook in `scripts/install_pre_commit_hook.py` to copy `change_log.md` to `docs/change_log.md` and stage it whenever the changelog is part of a commit (same pattern as the skills manifest regeneration). Consider whether `docs/docs.md` and `docs/index.md`, which duplicate README content, deserve the same treatment.

### 15. Fix the self-nesting docs site mirror
The `docs` target in the Makefile mirrors content with `cp -r documentation docs/` and `cp -r .agents docs/`. When the destination directory already exists, `cp -r` copies the source *into* it, so every `make docs` re-run without a prior `make clean` nests another copy: `docs/documentation/documentation/**` and `docs/.agents/.agents/**` exist in the repo today. Fix the target to remove (or `rsync --delete` into) the mirror subdirectories before copying, delete the committed nested trees, and confirm the Pages site still renders. Found during item 1, where the mirror also doubled the vector index (410 vs 219 chunks).

### 16. `pipeline_pass` frontmatter and dispatcher
Skills now declare a priority `tier:` (0 meta, 1 governance, 2 domain, 3 application) consumed by `SkillRouter`, `skills.json`, and the AGENTS.md manifest. Pipeline pass affinity is a separate concept and still open: add a distinct key (e.g. `pipeline_pass: 2` for reviewer skills like `cyber_security`) so the payload pipeline dispatcher injects each skill into the pass where it belongs (reviewer skills into pass 2, not pass 1) without colliding with the priority tier semantics.

### 17. Claude Code backend for pipeline tiers
Add a `claude_code` option to `payload_pipeline.tier_models`, handled before LiteLLM by shelling out to headless Claude Code (`claude -p "<prompt>" --output-format json`). Uses the subscription login instead of an API key; bills session usage per run. Best fit: Tier 1 judging. Note this item can only be exercised on a machine with Claude Code logged in.

### 18. Calibrate the skill router score threshold
All 38 skills now declare `triggers` frontmatter, which closed the deterministic routing gap. The semantic fallback is still uncalibrated: build a small labeled prompt set and tune `skill_router.score_threshold` (and possibly `top_k`) against it so semantic recall is measured rather than guessed.

### 19. OpenTelemetry integration
Integrate OpenTelemetry into the existing `system_logger.py` for advanced metrics and traces.

### 20. Homelab MCP server
Build a homelab MCP server to autonomously monitor, debug, and manage local Docker containers and network infrastructure. Per the global rules, present a pros/cons evaluation of the technology options before committing to an architecture.

### 21. Automated job hunting pipeline
Script an automated pipeline using web-search MCPs to scrape job postings, map against `USER_PROFILE.md`, and generate tailored resumes and cover letters. Follow the `career_assistant` skill's grounding rules (no fabricated experience).

## ✅ Completed

- **Ignore build artifacts and local state in git (done 2026-07-18):** `.gitignore` gained `/build/`, `*.egg-info/`, and `.telemetry/`; 60+ tracked artifacts (telemetry db, `build/lib/**`, installer binary, `__pycache__` caches, egg-info) untracked via `git rm --cached`. Go installer and editable pip install both rebuild cleanly with no new git noise. Spawned item 3 (tracked scratch files at the repo root).
- **Rebuild the vector index (done 2026-07-18):** fresh 219 chunk index over canonical sources only; `docs/` Pages mirror pruned from the scanner. Spot checks route security, debugging, IaC, and career prompts to the right skills. Spawned items 4 (idempotent rebuilds) and 15 (self-nesting docs mirror).
- **DevOps / IaC skill node (done 2026-07-17):** `.agents/skills/devops_sre/SKILL.md` exists; scope narrowed to Terraform/Kubernetes design during the 2026-07-18 skill refinement.
- **Skill routing recall gap for security prompts (done 2026-07-18):** all 38 skills declare `triggers` frontmatter; the failing prompt ("security hardening runbook for a FastAPI webhook server") now routes `cyber_security` deterministically. Threshold calibration continues as item 18.
- **Priority `tier` frontmatter (done 2026-07-18):** every SKILL.md declares `tier:` 0 to 3, parsed by `SkillRouter` and exposed in `skills.json` and the AGENTS.md manifest. See `documentation/skill_refinement_progress.md`. Pipeline pass affinity continues as item 16.
- **Skill library refinement (done 2026-07-18):** all 38 skills refined against a shared rubric, tiered, and cross deduplicated with Related Skills deferrals; tracked in `documentation/skill_refinement_progress.md`.
