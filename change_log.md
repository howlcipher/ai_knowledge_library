# Change Log

All notable changes to this project will be documented in this file.

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
* **ChromaDB Vector Integration**: Added `tools/build_vector_index.py` and `tools/semantic_search.py` to establish a local RAG system for intelligent, semantic knowledge retrieval.
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
* **Server Health Checks**: Refactored the stub in `tools/server_health_check.py` to expose a proper `main()` entrypoint, satisfying the automated test suite.

---

## [1.0.0] - 2026-07-07 (Initial Setup & Base Architecture)

### 🚀 Added
* Created standard Homelab Postmortem templates, GitHub profile sync tools, and local network architecture diagrams.
* Added standard GitHub Actions workflow for Markdown validation and Dependabot configuration.
* Built boilerplate templates for Python FastAPI and Go backend services inside `projects/templates/`.
* Engineered a beautiful, interactive Terminal User Interface (TUI) installer in Go using `charmbracelet/huh`.
* Built `scripts/setup_google_docs_auth.py` to provide an interactive OAuth setup flow for Google Docs API integration.
* Created `tools/fetch_security_news.py` to automatically update local docs with current cybersecurity threats.
* Added `.agents/skills/bug_bounty_hunter/SKILL.md` to establish strict methodologies for reconnaissance.

### 🛡 Security & Privacy
* Removed phone number from `USER_PROFILE.md` to protect Personally Identifiable Information (PII).
* Added `no_pii.md` global AGY rule and updated the `cyber_security` skill to strictly forbid handling sensitive PII.
* Implemented Secrets Management Architecture by creating strict AGY rules preventing hardcoded credentials.
* Created `.gitignore` and `.env.template` to establish a highly secure architecture for managing personal, off-repository secrets.

### 🤖 AGY Integrations & Memory
* Established `documentation/agent_memory/` for long-term AI persistent memory retention.
* Created `tools/brain.py` to allow offline CLI searching of the entire knowledge base.
* Added `.agents/rules/epistemic_skepticism.md` to enforce rigorous multi-source cross-checking.
* Built `.agents/rules/documentation_enforcement.md` to guarantee the AI always updates the changelog and README prior to any git push.
