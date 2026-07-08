# 📖 AI Knowledge Library - User Wiki & Guide

Welcome to the official User Guide for the AI Knowledge Library! This document outlines exactly what you can do with the library once you have it installed on your system.

---

## 1. 🎛️ The Main Control Panel (`ai_installer`)

The core of this library is managed entirely through the standalone `ai_installer` executable you downloaded during installation. It acts as your primary interactive menu.

Simply run `./ai_installer` in your terminal to bring up the menu. You can perform the following actions:

* **Install / Setup Environment:** Runs the initial setup, downloads dependencies, and safely links the global agent rules to your system.
* **Customize Profile:** Launches an interactive wizard that lets you generate or modify a `USER_PROFILE.md` file so the AI perfectly understands your preferences, name, and coding habits.
* **Launch RAG Interface:** Boot up either the fast **Terminal UI (TUI)** or the rich **Web UI** to chat securely with your codebase using Retrieval-Augmented Generation (RAG).
* **Sync / Update Repository:** Safely pull the latest rules and tools from GitHub without blowing away your local configurations.
* **Uninstall Global Links:** Cleanly detaches the AI skills from your global system environment.

---

## 2. 🤖 Chatting with your Codebase (RAG Interfaces)

You do not have to navigate the library through the command line to ask questions. You can chat with it! By selecting **"Launch RAG Interface (TUI/Web)"** from the `ai_installer` menu, you get two choices:

### 🖥️ Terminal UI (TUI)
* **What it is:** A blazing-fast, terminal-native chat interface built with Python `textual`.
* **Why use it:** It has full, unsandboxed access to your local filesystem.
* **Feature - Multi-LLM Switching:** From the TUI sidebar, you can hot-swap your AI provider on the fly. Don't like Gemini's answer? Switch to Claude 3.5 Sonnet, GPT-4o, Grok 2, or Perplexity Sonar instantly.

### 🌐 Web UI (Streamlit)
* **What it is:** A rich, graphical browser interface built with Python `streamlit`.
* **Why use it:** It runs in a secure browser sandbox, which is perfect for visually reviewing returned code snippets, markdown formatting, or diagrams.

---

## 3. 🛠️ Using the Embedded Developer Tools

The `tools/` directory contains powerful automation scripts that you (or an AI agent) can execute directly:

* **`python src/infrastructure/build_vector_index.py`**: Scans your entire knowledge base and builds a localized ChromaDB vector database so semantic RAG search works offline.
* **`python src/core/orchestrator.py "<query>"`**: Executes the Multi-Agent Orchestrator, deploying a Researcher and QA Reviewer agent to solve complex tasks with a secure Human-in-the-Loop proxy.
* **`python scripts/github_profile_sync.py`**: Automatically syncs your local profile variables against your live GitHub identity.
* **`python scripts/translate_project.py --lang [CODE]`**: Translates the documentation into any of the 13 supported global languages.
* **`python src/core/adversarial_tester.py`**: Runs a prompt-injection and adversarial logic test against your ruleset to ensure the AI behaves safely.

---

## 4. ✅ Local CI/CD (The Regression Guard)

If you intend to contribute or modify the library's rules yourself, you have access to a powerful local regression suite. 

Whenever you attempt to `git push` changes, a local hook intercepts the push and automatically runs:
```bash
make test lint build docs
```
This ensures that all Python tests, Go formatting rules, and API documentation generators pass perfectly before your broken code ever reaches GitHub Actions!

If you want to run this manually to check your work, just type:
```bash
make
```

---

*Need help fixing a broken environment? Check out the [Troubleshooting Guide](troubleshooting.md).*
