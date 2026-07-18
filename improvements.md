# 🚀 Future Automation and Feature Backlog

This document tracks all conceptual improvements, architectural upgrades, and automation tasks that can be implemented to further harden, scale, and optimize the AI Knowledge Library. 

## 📌 Planned Enhancements

- **Custom "DevOps / IaC" Skill Node:** Create `.agents/skills/devops_sre/SKILL.md` to define strict methodologies for Terraform, Kubernetes manifests, and CI/CD pipelines.
- **Custom Local MCP Servers:** Build a homelab MCP server to autonomously monitor, debug, and manage local Docker containers and network infrastructure.
- **Automated Job Hunting Pipeline:** Script an automated pipeline using web-search MCPs to scrape job postings, map against `USER_PROFILE.md`, and generate tailored resumes and cover letters.
- **Advanced Telemetry & Observability:** Integrate OpenTelemetry into the existing `system_logger.py` for advanced metrics and traces.

## 🔬 Payload Pipeline Findings (live runs, 2026-07-17)

Findings from running `--payload` end to end against local Ollama models (`qwen3:30b-a3b`, `llama3.1`, `qwen3:30b-instruct`). All three runs failed at pass 1; each failure exposed a concrete gap.

- **Separate transport failures from validation failures:** `litellm.APIConnectionError` (server crash, model not found, 600s timeout) surfaces as an empty response, which the gate scores as a `parse` failure and burns one of the three validation attempts. The persisted failed payload then reports `failure_vector: validation_gate.parse`, masking the real cause. Catch provider exceptions in the tier call path, retry them with backoff without consuming a validation attempt, and record a distinct error code (e.g. `UPSTREAM_UNAVAILABLE`) with the provider message in `error.context`.
- **Use provider enforced structured outputs where available:** `qwen3:30b-instruct` produced parseable JSON but invented fields on both real attempts (`lineage.history[0].action/details/timestamp`, then `critique.findings[0].description`). The VALIDATION ERROR feedback loop measurably improved attempt 2, but prompt discipline alone is weak on small local models. Ollama and LiteLLM support `response_format` with a JSON schema; passing `agent_task_payload.schema.json` (or a per pass subset) would make schema compliance mechanical instead of behavioral.
- **Make the LLM timeout configurable per tier:** the 30B model timed out at LiteLLM's default 600s while generating the full payload envelope. Add a `timeout` setting to `payload_pipeline` (or per entry in `tier_models`) and pass it through `litellm.completion`.
- **Preflight the provider before starting a run:** run 1 spent all three attempts against a crashed Ollama server, and run 2 against a model tag that had been removed mid session. A cheap ping (list models, verify the configured tag exists, one token generation) before pass 1 would fail fast with an actionable error.
- **Persist all attempt errors, not just the last:** the failed payload keeps only the final attempt's errors, so the schema violations from attempts 1 and 2 of run 3 are lost. Append a per attempt error history to `error.context` for post mortems.
- **Show exact object shapes in tier prompts or feedback:** the invented `lineage.history` fields suggest the model never saw the required entry shape. Embedding a one line example of each nested object (history entry, finding, adversarial test) in the tier prompts, or echoing the relevant schema fragment inside the VALIDATION ERROR feedback, would cut schema misses.
- **Close the skill routing recall gap for security prompts:** the run 3 prompt ("security hardening runbook for a FastAPI webhook server") routed zero skills — `cyber_security`/`blue_team` have no `triggers` frontmatter and their cross encoder scores fell below the 0.0 threshold. Add triggers (e.g. "hardening", "security audit", "vulnerability") to the security skills and consider calibrating `skill_router.score_threshold` against a small labeled prompt set.
- **Guard against oversized local models:** `qwen3:30b-a3b` crashed the Ollama server mid load (29GB RAM host). When the configured model is served by a local endpoint, surface the provider's error body (Ollama returns JSON error messages) instead of the generic connection error, so OOM/crash loops are diagnosable from the pipeline log.

## 🧭 Follow Ups From the Router and Pipeline Build (2026-07-17)

Items discussed during the skill router / payload pipeline work that are not yet implemented.

- **Claude Code backend for pipeline tiers:** add a `claude_code` option to `payload_pipeline.tier_models`, handled before LiteLLM by shelling out to headless Claude Code (`claude -p "<prompt>" --output-format json`). Uses the subscription login instead of an API key; bills session usage per run. Best fit: Tier 1 judging.
- **Rebuild the vector index:** `build_vector_index.py` was fixed to include dot directories (`.agents/skills/**` was invisible to the old glob), but the index has not been rebuilt since. Run it so semantic search can actually retrieve skill content.
- **Emit gate failures into telemetry:** the validation gate prints failures but does not log them through `telemetry_logger`, so schema failure rate per model is not yet a tracked metric (recommended in `documentation/multi_agent_payload_protocol.md`).
- **`tier` frontmatter for skills:** declare tier affinity in SKILL.md frontmatter (e.g. `tier: 2` for reviewer skills like `cyber_security`) so the pipeline dispatcher injects each skill into the pass where it belongs (reviewer skills into pass 2, not pass 1).
- **Install the pre-commit hook on other clones:** `.git/hooks` is not versioned; each machine needs a one time `python scripts/install_pre_commit_hook.py` (which now includes the skills manifest/index regeneration). Consider wiring it into `scripts/bootstrap.py` or the installer so it happens automatically.
