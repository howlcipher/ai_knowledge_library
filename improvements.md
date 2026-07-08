# 🚀 Future Automation and Feature Backlog

This document tracks all conceptual improvements, architectural upgrades, and automation tasks that can be implemented to further harden, scale, and optimize the AI Knowledge Library. 

## 1. Bug Fixes & Immediate Issues
* [x] **Test Pipeline Failures**: The initial `test_chromadb.py` mock test was structurally flawed, and `system_logger.py` was missing a `main()` entrypoint breaking `test_tools.py`. *(Update: Just fixed)*
* [x] **Crude Template Injector**: The `template_injector.py` uses crude Regex instead of the actual `Jinja2` templating engine requested.
* [x] **Go Spinner Output Suppression**: The TUI spinner suppresses standard error output on failures, making it hard for users to debug git cloning errors.
* [x] **ADR Naming Convention**: `generate_adr.py` doesn't enforce strict numerical ADR increments (e.g., ADR-001, ADR-002), risking naming collisions.

## 2. Architecture & Ease of Use
* [x] **Cobra CLI Refactor**: Refactor the Go Installer to use the `cobra` framework so power users can run `ai_installer install` directly from the command line without navigating the visual TUI.
* [x] **Centralized Config Loader**: Build a central `config.yaml` or `.env` configuration loader in Python. Currently, ChromaDB paths are hardcoded randomly across multiple scripts.
* [ ] **PgVector Migration**: Replace the local SQLite ChromaDB backend with a true PostgreSQL/pgvector database for production-level multi-agent concurrency.

## 3. Advanced Features & Tooling
* [x] **Streamlit / Gradio Web UI**: Build a visual browser-based chat interface connected directly to the RAG database, rather than relying exclusively on CLI agents.
* [x] **Automated Webhook Syncing**: Implement a FastAPI webhook endpoint that automatically triggers `sync_context.py` whenever the repository is pushed to.
* [x] **Web Scraping Upgrades**: The `web_research.py` tool is currently just a placeholder and needs real `BeautifulSoup` or `Selenium` logic implemented.
