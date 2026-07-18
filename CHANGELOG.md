# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- **Machine Readable Skills Index**: `scripts/generate_skills_manifest.py` now also emits `.agents/skills.json` (name, description, triggers, path per skill) with deterministic output, and the pre-commit hook from `scripts/install_pre_commit_hook.py` regenerates both the AGENTS.md manifest and the index automatically whenever a commit touches `.agents/skills/`. A parity test fails CI if the committed index drifts from the SKILL.md frontmatter.
- **Per Tier Model Config**: `payload_pipeline.tier_models` in `settings.yaml` assigns a different LiteLLM model to each tier (cheap drafting at Tier 3, strong judging at Tier 1), falling back to `llm_model` when unset.
- **Validation Gate Wiring**: New `src/core/validation_gate.py` implements the protocol gate (strict JSON parse, schema validation, sha256 verification, field mutation matrix diff, bounded retry with VALIDATION ERROR feedback, structured failed payloads). `Orchestrator.run_payload_loop` now runs the tiered 3 pass pipeline behind `payload_pipeline.enabled` in `settings.yaml` or the `--payload` CLI flag, using the tier prompts in `src/core/tier_prompts.py`, injecting SkillRouter results into `routing.skills`, and persisting each validated pass to `logs/payloads/<task_id>/`.
- **Skill Router**: New `src/core/skill_router.py` routes user prompts to relevant `.agents/skills/` SKILL.md files using deterministic frontmatter `triggers` plus cross encoder semantic scoring, injecting full skill bodies into the Orchestrator context with progressive disclosure and a configurable character budget (`skill_router` section in `settings.yaml`).
- **Skills Manifest Generator**: New `scripts/generate_skills_manifest.py` regenerates an auto generated skills table in `AGENTS.md` so agents without native skill discovery (Gemini CLI, Antigravity) get a cheap routing surface.
- **Graph-Based Orchestration**: Migrated the hand-rolled agent loop to a formal state machine using LangGraph.
- **Dependency Inversion Vector Store Architecture**: Created `BaseVectorStore` ABC, `VectorStoreFactory`, and explicit Chroma/PgVector backends.
- **Provider-Side Prompt Caching**: Injected explicit KV cache-control markers via LiteLLM for Anthropic/Gemini to reduce token costs.
- **Intelligent Failover & Rate Limit Handling**: Enhanced LiteLLM implementation to failover to backup LLMs when Gemini hits rate limits.
- **SAST Integration**: Integrated Bandit and GoSec into the CI/CD pipeline and patched 8 existing vulnerabilities.
- **Graphical Frontend**: Built an interactive Textual TUI and integrated Streamlit Web UI launchers natively into the Go installer.
- **Multi-LLM Integration Switch**: Implemented routing to dynamically swap between Claude, Gemini, GPT-4o, Grok, and Perplexity.
- **Automated Docker Registry Publishing**: Created a new GitHub Action workflow for GHCR.
- **LangSmith Tracing and Evaluation**: Native integration of LangSmith Client within `orchestrator.py` QA node to automatically track LangGraph agent trajectories and quantify QA rejection/approval rates over time.

### Changed
- **Project Structure**: Refactored the overloaded `tools/` directory into `src/core/`, `src/ui/`, `src/infrastructure/`, and `scripts/`.
- **Dependency & Configuration Security**: Replaced `requirements.txt` with `pyproject.toml`. Eradicated hardcoded secrets from `settings.yaml` and implemented `pydantic-settings`.
- **Data Persistence**: Updated `backup_library.py` to dynamically discover and backup PgVector or ChromaDB.
- **Docker Container Improvements**: Container no longer runs as root, utilizes multi-stage builds, and properly integrates Ollama in `docker-compose.yml`.

### Fixed
- **Vector Index Dot Directory Blind Spot**: `build_vector_index.py` used `glob`, which skips dot directories, so `.agents/` content was never indexed. Replaced with a pruned `os.walk` that includes `.agents` while skipping `.git`, `node_modules`, and build artifacts.
- **Memory Bug in Orchestrator**: Fixed an issue where the Researcher's previous draft was forgotten between QA cycles.
- **Webhook Concurrency Risk**: Fixed subprocess spawning in `webhook_server.py` to eliminate locking risks for SQLite.
- **PgVector Indexes**: Added missing `HNSW`/`IVFFlat` indexes in `pgvector_backend.py`.
- **Text Chunking**: Upgraded `TextChunker` from a crude word-count mechanism to LangChain semantic parsing.
- **Advanced RAG Capabilities**: Added Re-ranking, Query Expansion, and Hybrid Search capabilities.
- **Broken Imports & Regressions**: Resolved broken imports, merged duplicate configs, and eliminated redundant `sys.path.append` boilerplate.
- **Weak Human Proxy**: Improved the human-in-the-loop intercept from rudimentary regex to strict LLM Tool Calling schemas.
- **Tool Execution Logic**: Built out execution handling within `orchestrator.py` to route approved tool calls and pipe the resulting output back into the agent loop.
- **Deprecated Packages**: Migrated the legacy `google.generativeai` package to the newly supported `google.genai` SDK in `adversarial_tester.py`.
- **Silent Error Swallowing**: Replaced scattered `except Exception: pass` anti-patterns with proper logging and error handling across `brain.py`, `web_research.py`, and `tui.py`.
- **Naive Search**: Upgraded `LibrarySearcher` in `brain.py` to use semantic vector database infrastructure instead of naive string matching.
- **Subprocess Security**: Hardened subprocess calls in `backup_library.py`, `setup_cron.py`, and `celery_worker.py` by dynamically resolving absolute paths using `shutil.which` and `sys.executable`.
- **Linter Violations**: Cleaned up the codebase by removing unused imports and resolving PEP8 formatting issues.
