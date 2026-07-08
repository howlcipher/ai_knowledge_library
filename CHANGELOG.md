# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- **Graph-Based Orchestration**: Migrated the hand-rolled agent loop to a formal state machine using LangGraph.
- **Dependency Inversion Vector Store Architecture**: Created `BaseVectorStore` ABC, `VectorStoreFactory`, and explicit Chroma/PgVector backends.
- **Provider-Side Prompt Caching**: Injected explicit KV cache-control markers via LiteLLM for Anthropic/Gemini to reduce token costs.
- **Intelligent Failover & Rate Limit Handling**: Enhanced LiteLLM implementation to failover to backup LLMs when Gemini hits rate limits.
- **SAST Integration**: Integrated Bandit and GoSec into the CI/CD pipeline and patched 8 existing vulnerabilities.
- **Graphical Frontend**: Built an interactive Textual TUI and integrated Streamlit Web UI launchers natively into the Go installer.
- **Multi-LLM Integration Switch**: Implemented routing to dynamically swap between Claude, Gemini, GPT-4o, Grok, and Perplexity.
- **Automated Docker Registry Publishing**: Created a new GitHub Action workflow for GHCR.

### Changed
- **Project Structure**: Refactored the overloaded `tools/` directory into `src/core/`, `src/ui/`, `src/infrastructure/`, and `scripts/`.
- **Dependency & Configuration Security**: Replaced `requirements.txt` with `pyproject.toml`. Eradicated hardcoded secrets from `settings.yaml` and implemented `pydantic-settings`.
- **Data Persistence**: Updated `backup_library.py` to dynamically discover and backup PgVector or ChromaDB.
- **Docker Container Improvements**: Container no longer runs as root, utilizes multi-stage builds, and properly integrates Ollama in `docker-compose.yml`.

### Fixed
- **Memory Bug in Orchestrator**: Fixed an issue where the Researcher's previous draft was forgotten between QA cycles.
- **Webhook Concurrency Risk**: Fixed subprocess spawning in `webhook_server.py` to eliminate locking risks for SQLite.
- **PgVector Indexes**: Added missing `HNSW`/`IVFFlat` indexes in `pgvector_backend.py`.
- **Text Chunking**: Upgraded `TextChunker` from a crude word-count mechanism to LangChain semantic parsing.
- **Advanced RAG Capabilities**: Added Re-ranking, Query Expansion, and Hybrid Search capabilities.
- **Broken Imports & Regressions**: Resolved broken imports, merged duplicate configs, and eliminated redundant `sys.path.append` boilerplate.
- **Weak Human Proxy**: Improved the human-in-the-loop intercept from rudimentary regex to strict LLM Tool Calling schemas.
- **Naive Search**: Upgraded `LibrarySearcher` in `brain.py` to use semantic vector database infrastructure instead of naive string matching.
- **Subprocess Security**: Hardened subprocess calls in `backup_library.py`, `setup_cron.py`, and `celery_worker.py` by dynamically resolving absolute paths using `shutil.which` and `sys.executable`.
- **Linter Violations**: Cleaned up the codebase by removing unused imports and resolving PEP8 formatting issues.
