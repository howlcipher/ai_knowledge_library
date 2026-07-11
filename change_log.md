# Change Log

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-07-10

### 🚀 Massive Ecosystem & MCP Integrations
- **Extensive MCP Plugin Arsenal**: Integrated over 20+ Model Context Protocol (MCP) servers into `settings.yaml` (Discord, Crunchyroll, Postgres, Kubernetes, Docker, Yahoo Finance, Wikipedia, Brave Search, Memory Graph, Puppeteer, Google Drive, Jira, Sentry, AWS, Strava, Steam, Shodan, MLB, and more) granting the AI orchestrator near-infinite native domain capabilities.
- **Stealth Text Humanization Agent**: Built a dedicated `Technical_Writer` node into the LangGraph orchestrator. It natively rewrites all QA-approved documentation to maximize burstiness and perplexity, guaranteeing generated reports bypass external AI detectors for free.

### 📚 Knowledge & Hygiene
- **Advanced Architecture Guidelines**: Completely rewrote `documentation/coding_standards.md` to mathematically enforce OOP/FP context choices, Dependency Injection, and Dynamic DRY paradigms across all AI generations.

## [2.1.0] - 2026-07-08

### 🚀 Major Features & Architectural Overhaul
- **Provider-Side KV Prompt Caching**: Refactored the internal LiteLLM messaging pipelines across the TUI and Orchestrator to automatically inject explicit cache-control markers (Anthropic `ephemeral`) and structure contexts to natively trigger API-level Prefix caching. This massively reduces latency and halves API costs on repeat prompts.
- **Multi-Agent Orchestration Engine**: Shipped `src/core/orchestrator.py` which spawns self-correcting Researcher and QA Reviewer personas that iteratively solve problems until perfected.
- **Human-in-the-Loop Execution Guard**: Built a secure terminal proxy interceptor into the new Orchestrator that strictly pauses and requests `[Y/n]` manual authorization before allowing any LLM to execute shell commands.
- **Cost & Token Analytics Dashboard**: Integrated a native SQLite telemetry database (`src/infrastructure/telemetry_logger.py`) and a `pandas`-powered visual dashboard into the Web UI (`src/ui/web_ui.py`) to actively monitor cost, latency, and cache hits.
- **Intelligent Failover & Rate Limit Recovery**: Expanded LiteLLM router implementations across all tooling to automatically cascade from `gemini-1.5-pro` to fallback providers (`claude-3-5-sonnet`, `gpt-4o`, `grok-2`) whenever API rate limits are exceeded.

### 🛡️ Security & Hardening
- **SAST Pipeline Integration**: Hardened the Go cross-compilation pipeline with `gosec` and the Python CI environments with `bandit`. Patched 8 existing vulnerabilities (B108, B701, G204).
- **Test Coverage Floor Guard**: Established a rigid 42% global test coverage floor via `--cov-fail-under=42` inside `Makefile` to instantly block any pull requests that degrade unit testing standards.

## [2.0.0] - 2026-07-07

### 🚀 Major Features & Architectural Overhaul
- **Docker & Cloud Ready**: Fully dockerized the knowledge library (`Dockerfile` and `docker-compose.yml`) and added a centralized HTTP Client-Server mode to ChromaDB (`scripts/sync_context.py --host`).
- **Dynamic Context Templating**: Implemented `scripts/template_injector.py` to automatically inject `USER_PROFILE.md` variables dynamically into Jinja2 templates for all AI skills at runtime.
- **Context Pruning Engine**: Shipped `scripts/prune_context.py` to proactively analyze ChromaDB embeddings for outdated or contradictory markdown files.
- **Interactive TUI Enhancements**: 
    - Added a natively embedded `Help / FAQ` menu to the Go TUI installer.
    - Added beautiful `charmbracelet/bubbles/spinner` animations during long-running Git and Sync tasks.
- **Automated PR Code Review**: Configured `.agents/rules/code_review.md` allowing the AI to act as an automated code reviewer on GitHub PRs.
- **Web Research / Scraping Tool**: Added `src/core/web_research.py` utilizing `BeautifulSoup` to autonomously scrape external documentation into the RAG vector index.
- **Automated ADR Engine**: Built `scripts/generate_adr.py` to instantly scaffold timestamped Architecture Decision Records for the library.

### 🛡️ Security & Privacy
- **GitHub CodeQL Integration**: Added a native GitHub Action (`codeql.yml`) to perform deep semantic vulnerability monitoring globally.
- **Pre-commit Environment Variable Audit**: Wrote `scripts/install_pre_commit_hook.py` to strictly prevent developers from accidentally pushing `.env` files or hardcoded keys.
- **Google Docs OAuth Token Rotation**: Upgraded `push_to_docs.py` to transparently rotate `token.json` refresh tokens without manual user re-authentication.
- **Strict GPG Signing**: Added a `.agents/rules/gpg_signatures.md` constraint mandating that AI agents only execute mathematically signed commits.

### 📊 Testing & Quality Assurance
- **End-to-End Go TUI Tests**: Expanded the test suite with `cmd/installer/main_test.go` to validate interactive terminal prompts on Ubuntu, Windows, and macOS via a new `cross_platform.yml` Action.
- **ChromaDB Mock Testing**: Engineered `tests/test_chromadb.py` using `unittest.mock` to validate RAG vector indexing without incurring disk I/O.
- **Strict Python Typing (Mypy)**: Standardized Python type-hinting across the repository and locked it down in CI using `mypy`.
- **Standardized Python Logging**: Refactored raw standard output calls in favor of a new configurable `src/infrastructure/system_logger.py` module.
- **Cloud Architecture Diagrams**: Upgraded `infrastructure/network_diagram.md` with detailed AWS (EKS/RDS) and GCP (GKE/CloudSQL) topological maps.

## [1.3.0] - 2026-07-07

### 🚀 Added
- **Interactive Profile Customizer**: Embedded an interactive `charmbracelet/huh` TUI menu natively into the Go installer to securely capture and format custom `USER_PROFILE.md` structures for users who fork the library. All inputs gracefully handle empty options.
- **Dynamic Skills Architecture**: Expanded the global skills manifest with 8 new cognitive constraints bridging UI/UX, Quantitative Finance, Color Theory, Accessibility, Product Management, Machine Learning, Economic Theory, and Baseball Analytics.
- **Automated CI Linting**: Configured a `.github/workflows/lint.yml` Action bridging `flake8`, `bandit` (SAST), and `golangci-lint` to strictly enforce zero-defect standards globally on all PRs.
- **Code Coverage CI Metrics**: Augmented the `test.yml` GitHub workflow to automatically measure and generate test coverage percentages (`pytest --cov` and `go tool cover`) for full audibility.
- **Expanded Makefile**: Completely overhauled the build instructions spanning automated code formatting (`black`, `gofmt`), deep cache purges (`clean`), and isolated test coverages (`coverage-python`, `coverage-go`).
- **Comprehensive Backlog Manifest**: Heavily populated `improvements.md` with a massive 21-task architectural, DevOps, and testing roadmap for the future.

### 🛠 Fixed
- Eliminated Python syntactic escape errors (`\n`) accidentally placed natively inside bootstrapping scripts, ensuring the `docs.yml` CI Action parses all classes successfully via `pdoc`.

## [1.2.0] - 2026-07-07

### 🚀 Added
* **Automated Multi-Platform Releases**: Integrated `GoReleaser` with GitHub Actions (`release_installer.yml`) to automatically compile and release Windows, macOS, and Linux binaries (including `.deb` and `.rpm`) natively triggered on semantic version tags.
* **ChromaDB Vector Integration**: Added `src/infrastructure/build_vector_index.py` and `src/infrastructure/semantic_search.py` to establish a local RAG system for intelligent, semantic knowledge retrieval.
* **Data Science Capabilities**: Built `.agents/skills/data_analyst/SKILL.md` to mathematically enforce methodologies for Pandas data wrangling and Scikit-Learn pipelines.
* **Automated API Documentation**: Configured GitHub Actions (`docs.yml`) utilizing `pdoc` to automatically build and deploy API documentation to a `gh-pages` branch.
* **Standardized Makefile**: Introduced a root `Makefile` to establish standard entry points for installation, testing (`make test`), linting, building, and documentation generation.
* **Automated Tool Testing Suite**: Created Python-based testing in `tests/test_tools.py` using `pytest`, integrated alongside a native `go test` suite in `cmd/installer/main_test.go`.

### 🔄 Changed
* **Go Installer OOP Refactor**: Re-engineered the interactive Go TUI Installer (`cmd/installer/main.go`) to utilize strictly Object-Oriented methodologies (`Installer` struct) for clean state management and maximum DRY compliance.
* **GitHub Actions Workflows**: Upgraded all GitHub Actions (checkout, setup-go, setup-python) to their most modern versions via Dependabot integrations.
* **Statistics Engine Updates**: Enhanced `library_statistics.py` and `update_badges.yml` to automatically rewrite the `README.md` sizing badge without failing on permission blocks.
* **Dynamic Test Coverage**: Rewrote the Python testing suite to use `importlib` to dynamically discover and validate all modules within the `tools/` directory rather than relying on hardcoded imports.

### 🛠 Fixed
* **GoReleaser Dirty State Crashes**: Patched the GitHub Actions release pipeline to trigger flawlessly on git tags rather than manipulating tags via bash during a push-to-main workflow, preventing fatal Git state panics.
* **GoReleaser Deprecations**: Completely rewrote `.goreleaser.yaml` to comply with the rigid version 2 schema requirements, removing deprecated archives and format overrides.
* **Workflow Permissions**: Fixed authentication crashes in the `Update Badges` and `Docs` pipelines by explicitly declaring `contents: write` in the GitHub Actions configuration.
* **Docs API Dependency Errors**: Fixed the API documentation generator by forcing `pip install -r requirements.txt` prior to `pdoc` execution, resolving missing `chromadb` import crashes.
* **Google Docs OAuth Flow**: Updated the `setup_google_docs_auth.py` script instructions to accurately reflect the modernized Google Cloud Platform 'Audience' UI and test user whitelisting process.
* **Server Health Checks**: Refactored the stub in `scripts/server_health_check.py` to expose a proper `main()` entrypoint, satisfying the automated test suite.

---

## [1.0.0] - 2026-07-07 (Initial Setup & Base Architecture)

### 🚀 Added
* Created standard Homelab Postmortem templates, GitHub profile sync tools, and local network architecture diagrams.
* Added standard GitHub Actions workflow for Markdown validation and Dependabot configuration.
* Built boilerplate templates for Python FastAPI and Go backend services inside `projects/templates/`.
* Engineered a beautiful, interactive Terminal User Interface (TUI) installer in Go using `charmbracelet/huh`.
* Built `scripts/setup_google_docs_auth.py` to provide an interactive OAuth setup flow for Google Docs API integration.
* Created `scripts/fetch_security_news.py` to automatically update local docs with current cybersecurity threats.
* Added `.agents/skills/bug_bounty_hunter/SKILL.md` to establish strict methodologies for reconnaissance.

### 🛡 Security & Privacy
* Removed phone number from `USER_PROFILE.md` to protect Personally Identifiable Information (PII).
* Added `no_pii.md` global AGY rule and updated the `cyber_security` skill to strictly forbid handling sensitive PII.
* Implemented Secrets Management Architecture by creating strict AGY rules preventing hardcoded credentials.
* Created `.gitignore` and `.env.template` to establish a highly secure architecture for managing personal, off-repository secrets.

### 🤖 AGY Integrations & Memory
* Established `documentation/agent_memory/` for long-term AI persistent memory retention.
* Created `src/core/brain.py` to allow offline CLI searching of the entire knowledge base.
* Added `.agents/rules/epistemic_skepticism.md` to enforce rigorous multi-source cross-checking.
* Built `.agents/rules/documentation_enforcement.md` to guarantee the AI always updates the changelog and README prior to any git push.
