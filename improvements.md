# 🚀 Future Automation and Feature Backlog

This document tracks all conceptual improvements, architectural upgrades, and automation tasks that can be implemented to further harden, scale, and optimize the AI Knowledge Library. 

## 1. CI/CD & DevOps Automation
* [x] **Automated Linting Pipeline**: Add `golangci-lint` (Go) and `flake8`/`black` (Python) to a new GitHub Action (`lint.yml`) to rigorously enforce styling constraints before tests even run.
* [x] **Static Application Security Testing (SAST)**: Integrate `gosec` (for Go) and `bandit` (for Python) into the CI pipeline to automatically scan for hardcoded secrets, injection vulnerabilities, and bad cryptographic practices on every push.
* [x] **CodeQL Integration**: Add GitHub's native CodeQL semantic code analysis workflow to monitor for advanced security vulnerabilities globally.
* [x] **Dockerized Environment**: Create a root `Dockerfile` and `docker-compose.yml` to allow users to spin up the entire knowledge library environment (including ChromaDB, Python, and Go) in a strictly isolated, reproducible container.
* [x] **Cross-Platform Install Testing**: Build GitHub Actions that actually spin up Windows, macOS, and Ubuntu VMs to execute the installer binaries and shell scripts to guarantee zero regressions.

## 2. Testing & Quality Assurance
* [x] **Code Coverage Reporting**: Upgrade `test.yml` to generate coverage metrics (e.g., `pytest --cov`, `go test -cover`) and output them in the CI runner.
* [x] **End-to-End (E2E) Installer Tests**: Implement automated integration tests that simulate a user navigating the Go TUI (`charmbracelet/huh`) to ensure the interactive installer flow never breaks.
* [x] **ChromaDB Mock Testing**: Build mock database interfaces in the Python test suite to validate the RAG Semantic Search and Vector Indexing scripts without requiring disk I/O.
* [x] **Makefile Expansion**: Expand the `Makefile` with `make lint`, `make format`, `make clean`, and `make coverage` targets for a highly standardized local developer experience.

## 3. Architecture & Code Quality
* [x] **Strict Python Typing**: Refactor all Python scripts in `tools/` and `scripts/` to use strict type hints (`typing` module) and validate them via `mypy`.
* [x] **Standardized Logging**: Replace all raw `print()` statements in Python scripts with the native `logging` module, allowing for configurable log levels (INFO, DEBUG, ERROR) and file-based log rotation.
* [x] **Go TUI Spinners**: Integrate `charmbracelet/bubbles/spinner` into the Go installer to display beautiful loading animations during long-running tasks like cloning and downloading dependencies.
* [x] **Client-Server ChromaDB**: Upgrade the vector indexing tool to support connecting to a centralized, containerized ChromaDB server via HTTP, rather than relying solely on local SQLite files. This allows multiple machines to query the same brain.

## 4. Agent Tooling & RAG (Retrieval-Augmented Generation)
* [x] **Dynamic Context Templating**: Build a Jinja2 script that dynamically injects data from `USER_PROFILE.md` directly into the agent `SKILL.md` files at runtime, so the AI never reads placeholder variables.
* [x] **Automated PR Review Bot**: Create a `.agents/rules/code_review.md` rule and wire the AI to automatically review and comment on Pull Requests when integrated as a GitHub App.
* [x] **Web Scraping / Research Tool**: Add a Python tool (`tools/web_research.py`) utilizing `BeautifulSoup` to allow the AI to scrape external documentation and automatically append it to the vector database.
* [x] **Context Pruning Engine**: Develop a script that analyzes the ChromaDB vector embeddings and automatically flags redundant, contradictory, or outdated markdown files for manual review.

## 5. Security & Privacy
* [x] **Google Docs OAuth Token Rotation**: Enhance `push_to_docs.py` with automatic, silent refresh token rotation logic so the user never has to re-authenticate manually when the token expires.
* [x] **Environment Variable Auditing**: Build a pre-commit hook that explicitly searches for accidental `.env` file additions or high-entropy strings (potential API keys) before allowing a `git push`.
* [x] **GPG Signature Enforcement**: Configure the repository and the AI agent's commit rules to strictly require mathematically signed (GPG/SSH) commits for identity verification.

## 6. Documentation & Onboarding
* [x] **Interactive Troubleshooting Guide**: Add a `documentation/troubleshooting.md` file cataloging solutions to common Python virtual environment (venv) failures, Go binary execution errors, and Git rebase conflicts.
* [x] **Cloud Architecture Diagrams**: Expand `infrastructure/network_diagram.md` to map out cloud environments (AWS/GCP/Terraform) rather than just the local homelab.
* [x] **Automated ADR Generation**: Build a script that scaffolds out blank Architecture Decision Records (ADRs) with timestamped metadata and auto-updates an ADR index whenever a new decision is logged.
* [x] **TUI "Help" Menu**: Add an interactive Help/FAQ tab natively within the Go installer TUI so users can debug issues directly from the terminal without opening a browser.
