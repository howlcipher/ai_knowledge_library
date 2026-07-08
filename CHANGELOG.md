# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] _ 2026_07_07

### Added
* LLM Verification Layer: Integrated Gemini into `web_research.py` to evaluate the authenticity of scraped text before it is inserted into the vector database.
* Comprehensive Test Suite: Added robust pytest test suites for configuration, frontend DOM elements, and the Python tools library.
* TUI Profile Customizer: Added an interactive Profile Customization TUI to the main Go installer.
* GitHub Actions & CI/CD: Implemented workflows for GoReleaser cross_platform builds, automated linting, SAST scanning, code coverage, and Markdown validation.
* Web Frontend: Built a visually stunning retro mecha anime themed landing page for GitHub Pages with a custom SVG favicon, OS download links, and a direct repository link.
* Accessibility & i18n: Added theme toggling (Light/Dark mode), a dedicated Colorblind mode, and dynamic internationalization translations to the landing page frontend.
* Advanced Domain Skills: Added over 17 new agentic skill modules covering design, quantitative finance, cybersecurity (red/blue team), and technical writing.
* Streamlit RAG Web UI: Built a visual browser_based chat interface connected directly to the RAG database.
* Automated Webhook Syncing: Implemented a FastAPI webhook endpoint that automatically triggers `sync_context.py` whenever the repository is pushed to.

### Changed
* Mass Refactoring (OOP & DRY): Completely overhauled all Python tools and scripts to utilize Object_Oriented Programming. Separated frontend logic into modular `app.js` files and implemented a centralized configuration loader.
* Documentation Overhaul: Restructured the `README.md` to include visual badges, flair, and clear Purpose and Value statements.
* Cobra CLI Refactor: Refactored the Go Installer to use the `cobra` framework so power users can run `ai_installer install` directly from the command line.
* PgVector Migration: Migrated from a local SQLite ChromaDB backend to a true PostgreSQL/pgvector database for production_level multi_agent concurrency.

### Fixed
* Release Workflows: Fixed GoReleaser dirty state errors by configuring the action to trigger exclusively on tags rather than direct pushes to main.
* Go Spinner Compilation Bug: Fixed an issue where the Go TUI spinner was suppressing standard error output during git clone failures.
* Test Pipeline Failures: The initial `test_chromadb.py` mock test was fixed, and `system_logger.py` was given a `main()` entrypoint to fix pytest collection errors.
* Crude Template Injector: The `template_injector.py` was updated to use the actual `Jinja2` templating engine to avoid brittle regex parsing.
* ADR Naming Convention: `generate_adr.py` now enforces strict numerical ADR increments (e.g., ADR_001, ADR_002) to prevent naming collisions.
* CI Badge Synchronization: Fixed badge update workflows by granting repository write permissions and enabling proper main branch snapshot releases.
