# 🚀 Future Automation and Feature Backlog

This document tracks all conceptual improvements, architectural upgrades, and automation tasks that can be implemented to further harden, scale, and optimize the AI Knowledge Library. 

## 1. Project Layout & Architecture Conflation (High Priority)
* **`tools/` Dumping Ground Refactor**: The `tools/` directory is overloaded, mixing domain logic (`orchestrator.py`), UI layers (`web_ui.py`), database backends, and admin scripts. Needs restructuring into `src/core/`, `src/ui/`, `src/infrastructure/`, and `scripts/`.
* **Violation of Dependency Inversion**: Vector database routing (`pgvector` vs `chromadb`) uses explicit `if/else` checks across files instead of a unified `BaseVectorStore` Abstract Base Class (ABC).
* **Broken Web UI Integration**: `web_ui.py` hardcodes `chromadb.PersistentClient`. If `pgvector` is enabled in settings, the Web UI completely ignores it and searches outdated local Chroma data.

## 2. Advanced RAG & Vector Limitations
* **Missing PgVector Indexes**: `pgvector_backend.py` misses `HNSW` or `IVFFlat` indexes, forcing exact nearest neighbor full-table scans.
* **Naive Text Chunking**: `TextChunker` uses a crude word-counting mechanism that fractures semantic meaning and lacks chunk overlap. Needs LangChain/LlamaIndex semantic parsers.
* **Missing Advanced Capabilities**: Lacks Re-ranking (Cohere/BGE), Query Expansion, and Hybrid Search (BM25 + Vector).

## 3. Multi-Agent Orchestration Flaws
* **Critical Memory Bug in Orchestrator**: In `orchestrator.py`, the `QA_Reviewer`'s feedback is passed to the `Researcher`, but the `Researcher`'s *own previous draft* is forgotten, forcing it to regenerate from scratch.
* **Graph-Based Orchestration Migration**: The hand-rolled agent loop is rigid. Migrate to a formal state machine like LangGraph, AutoGen, or CrewAI.
* **Weak Human Proxy**: The human-in-the-loop intercept uses rudimentary regex for bash blocks instead of strict LLM Tool/Function Calling schemas.

## 4. Dependency & Configuration Security
* **Dangerous Dependencies**: `requirements.txt` mixes dev tools with production, lists duplicates, and lacks version pinning. Implement `Poetry` or `uv`.
* **Hardcoded Secrets**: `settings.yaml` contains plain-text passwords and `os.environ.get("GEMINI_API_KEY")` is queried arbitrarily. Implement a centralized loader like `pydantic-settings`.

## 5. DevOps & Infrastructure (`devops`)
* **Useless Docker Container**: `Dockerfile` runs as root, lacks multi-stage build, and immediately exits after `sync_context.py`.
* **Missing Ollama Integration**: `docker-compose.yml` lacks the local Ollama service definition needed for true offline air-gapped support.
* **Webhook Concurrency Risk**: `webhook_server.py` spawns `subprocess.Popen` without a background queue, creating a DoS/locking risk for SQLite. Needs Celery/Redis RQ.
* **Telemetry SQLite Mutex / Integrity**: The SQLite database lacks a mutex and is located in the home directory, while Chroma is in the workspace. We need to unify persistence directories.
* **Automated Docker Registry Publishing**: Create a new GitHub Action workflow to automatically build and push the library's Docker container to GHCR.

## ✅ Recently Completed
* **Provider-Side Prompt Caching:** Refactored TUI and Orchestrator prompts to front-load static system contexts and injected explicit KV cache-control markers via LiteLLM for Anthropic/Gemini, significantly reducing token processing costs and latency.
* **Multi-Agent Orchestration:** Created `tools/orchestrator.py` implementing a collaborative loop between Researcher and QA Reviewer personas with a strict Human Proxy interceptor for executable commands.
* **Intelligent Failover & Rate Limit Handling:** Enhanced LiteLLM implementation across the library to automatically cascade and failover to backup LLMs (Claude, GPT-4o) when Gemini hits rate limits.
* **SAST Integration & Security Hardening:** Integrated Bandit and GoSec into the CI/CD pipeline and patched 8 existing vulnerabilities (B108, B701, G204).
* **Graphical Frontend (TUI or Web UI):** Built an interactive Textual TUI (`tui.py`) and integrated Streamlit Web UI launchers natively into the Go installer.
* **Multi-LLM Integration Switch:** Implemented `litellm` routing and a configuration interface inside the TUI to dynamically swap between Claude, Gemini, GPT-4o, Grok, and Perplexity.
