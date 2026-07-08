# 🐛 Known Issues and Bugs

This document tracks known flaws, bugs, and broken items across the project that need to be resolved. Fixing these should be prioritized independently of new features.

## 1. Orchestrator Missing Tool Execution Logic (Critical)
* **Location:** `src/core/orchestrator.py`
* **Issue:** The LangGraph orchestrator correctly parses tool calls (like `execute_bash_command`) and successfully runs the `human_proxy_intercept` to ask the user for permission. However, if the user approves, it merely prints `[Executing N tool calls...]` and lacks the actual execution logic to run the command and feed the result back into the agent loop.

## 2. Deprecated `google.generativeai` Package (High)
* **Location:** `src/core/adversarial_tester.py` (and potentially others)
* **Issue:** The project uses `google.generativeai` which has officially ended support and will no longer receive bug fixes. The codebase must be migrated to the new `google.genai` package.

## 3. Silent Error Swallowing (Try-Except-Pass) (Medium)
* **Location:** `src/core/brain.py`, `src/core/web_research.py`, `src/ui/tui.py`, `scripts/generate_agent_summary.py`
* **Issue:** Bandit SAST scanner flagged multiple instances of `except Exception: pass` (B110). This anti-pattern silently swallows errors, causing silent failures that are extremely difficult to debug. These should be replaced with proper error logging or handling.

## 4. Naive Local Search Implementation (Medium)
* **Location:** `src/core/brain.py`
* **Issue:** The `LibrarySearcher` implements a naive `os.walk` line-by-line string matcher. This completely ignores the semantic vector database (Chroma/PgVector) infrastructure. It should either be deprecated or upgraded to utilize semantic search.

## 5. Unresolved `sys.path.append` Boilerplate (Low)
* **Location:** `src/core/brain.py`, `src/core/adversarial_tester.py`
* **Issue:** The `CHANGELOG.md` states that redundant `sys.path.append(repo_root)` boilerplate was eliminated, but it is still actively present in these files.

## 6. Subprocess Security & Partial Paths (Low)
* **Location:** `scripts/backup_library.py`, `scripts/setup_cron.py`, `src/infrastructure/celery_worker.py`
* **Issue:** Bandit (B607/B603) flagged `subprocess.run` calls that use partial executable paths (e.g., `crontab`, `pg_dump`). While mostly safe in this controlled environment, using absolute paths or validating input is better security practice.

## 7. Linter Violations & Unused Imports (Low)
* **Location:** Multiple files
* **Issue:** Flake8 reports numerous unused imports (e.g., `stat` in `install_pre_push_hook.py`, `pydantic.Field` in `config_loader.py`, `chromadb` in `web_ui.py`) and various PEP8 line-length/whitespace violations.
