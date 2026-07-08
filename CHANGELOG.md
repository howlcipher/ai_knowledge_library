# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] _ 2026_07_07

### Fixed
* Test Pipeline Failures: The initial `test_chromadb.py` mock test was fixed, and `system_logger.py` was given a `main()` entrypoint.
* Crude Template Injector: The `template_injector.py` was updated to use the actual `Jinja2` templating engine.
* Go Spinner Output Suppression: The TUI spinner was updated to no longer suppress standard error output on failures.
* ADR Naming Convention: `generate_adr.py` now enforces strict numerical ADR increments (e.g., ADR_001, ADR_002) to prevent naming collisions.

### Changed
* Cobra CLI Refactor: Refactored the Go Installer to use the `cobra` framework so power users can run `ai_installer install` directly from the command line.
* Centralized Config Loader: Built a central configuration loader in Python to replace hardcoded ChromaDB paths.
* PgVector Migration: Replaced the local SQLite ChromaDB backend with a true PostgreSQL/pgvector database for production_level multi_agent concurrency.

### Added
* Streamlit / Gradio Web UI: Built a visual browser_based chat interface connected directly to the RAG database.
* Automated Webhook Syncing: Implemented a FastAPI webhook endpoint that automatically triggers `sync_context.py` whenever the repository is pushed to.
* Web Scraping Upgrades: Upgraded the `web_research.py` tool with real `BeautifulSoup` logic.
