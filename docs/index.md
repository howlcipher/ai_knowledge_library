<div align="center">
  <img src="assets/cyberpunk_hybrid_banner.jpg" alt="Retro CLI Banner" width="800" />
  <br><br>
  <img src="https://img.shields.io/static/v1?label=AI&message=Knowledge_Library&color=blueviolet&style=for_the_badge" alt="AI Library Badge" />
  <img src="https://img.shields.io/static/v1?label=Library_Size&message=386&color=success&style=for_the_badge" alt="Library Size Badge" />
  <img src="https://img.shields.io/static/v1?label=Powered_By&message=Antigravity&color=blue&style=for_the_badge&logo=google" alt="Antigravity Badge" />
</div>

<h1 align="center">Personal AI Knowledge Library</h1>

<p align="center">
  <img src="https://img.shields.io/static/v1?label=Language&message=Python&color=3776AB&style=flat_square&logo=python" alt="Python Badge" />
  <img src="https://img.shields.io/static/v1?label=Language&message=Go&color=00ADD8&style=flat_square&logo=go" alt="Go Badge" />
  <img src="https://img.shields.io/static/v1?label=Platform&message=Docker&color=2496ED&style=flat_square&logo=docker" alt="Docker Badge" />
  <img src="https://img.shields.io/static/v1?label=OS&message=Linux&color=FCC624&style=flat_square&logo=linux" alt="Linux Badge" />
</p>

<p align="center">
  <a href="https://github.com/howlcipher/ai_knowledge_library/actions/workflows/release_installer.yml"><img src="https://github.com/howlcipher/ai_knowledge_library/actions/workflows/release_installer.yml/badge.svg" alt="Release Installer" /></a>
  <a href="https://github.com/howlcipher/ai_knowledge_library/actions/workflows/test.yml"><img src="https://github.com/howlcipher/ai_knowledge_library/actions/workflows/test.yml/badge.svg" alt="Tests" /></a>
  <a href="https://github.com/howlcipher/ai_knowledge_library/actions/workflows/docs.yml"><img src="https://github.com/howlcipher/ai_knowledge_library/actions/workflows/docs.yml/badge.svg" alt="Docs" /></a>
</p>
***

> This repository serves as the central context layer for terminal AI agents. It maps directly into the CLI to enforce coding standards, eliminate hallucinations, and provide deep architectural context tailored specifically for William Elias.

***

## 🧠 Core Value Proposition

### 📚 Quick Start: [Read the Official User Wiki & Guide](documentation/USER_GUIDE.md)

**What it is:** A centralized, filesystem-based knowledge library and execution environment specifically engineered for AI agents operating within the terminal.

**The Engineering Value:** AI agents frequently hallucinate or generate generic boilerplate when operating blindly. By linking this structured library to your local environment, you mathematically force the AI to operate exactly like a senior engineer on your team. The immediate benefits include:
* **Zero-Hallucination Architecture:** The AI is strictly bound by local markdown rules, coding standards, and project constraints before generating code.
* **Automated QA & Guardrails:** Built-in CI/CD pipelines (SAST, Linting, Testing) ensure the AI cannot break the master branch.
* **Domain-Specific Expertise:** Pre-loaded domain skills (e.g., UI/UX, Data Science, Security) allow the AI to adapt its logic to the specific task rather than guessing.

### 🔌 The Model Context Protocol (MCP) Advantage
**Why is MCP important?** Historically, AI models have been trapped in a sandbox, limited only to their outdated training data and what you type in the chat box. Writing custom integrations for every external service (like Jira, AWS, or Wikipedia) required hundreds of lines of brittle code. 

**The MCP Solution:** This library leverages the new open standard **Model Context Protocol** to act as a massive orchestration engine. By simply adding community-built MCP plugins to the `settings.yaml`, your AI instantly gains autonomous "hands" and "senses":
* **Real-Time Knowledge:** The AI can query **Wikipedia**, **Brave Search**, and **Yahoo Finance** natively to bypass the "knowledge cutoff" problem.
* **Full Autonomy:** The Orchestrator is armed with **Docker, Kubernetes, AWS, GitLab, Shodan, Puppeteer, Sentry, and Jira**. You can command it to find a bug in Jira, spin up a headless browser to reproduce it, fix the local code, and push the commit.
* **Cognitive Persistence:** Powered by the **Memory** and **Sequential Thinking** MCPs, the agent permanently remembers your project preferences and can break down complex math or debugging loops step-by-step.

### 🛡️ Security, Privacy & Trust
When giving an AI access to your local filesystem and commands, security is paramount. This library is designed from the ground up to protect your local environment from prompt injection, AI poisoning, and hallucinated actions:
* **Anti-Poisoning & Grounding Protocol:** The AI is mathematically grounded in local rule files (like [`GEMINI.md`](GEMINI.md)) and forced to apply an epistemic humility decision tree. If live data conflicts with stale data, or if an action violates the [`anti_manipulation.md`](.agents/rules/anti_manipulation.md) constraints, the Orchestrator will automatically halt.
* **Strict Human-in-the-Loop:** Absolutely no executable commands (like `bash` scripts or destructive API calls) are run without explicit human consent. You will see exactly what the AI wants to run and can approve or reject it natively.
* **100% Local Privacy:** The Orchestrator and vector databases (ChromaDB / PGVector) run entirely locally. Your local filesystem, secrets, and project architecture are never ingested into a third-party training set.

***

## 🌍 Localizations & Languages
The AI Knowledge library supports language modules. The AI will translate operations and the Go TUI installer supports native execution in the following languages:

* [🇺🇸 US English](documentation/languages/README_en_US.md) (Default)
* [🇬🇧 UK English](documentation/languages/README_en_UK.md) | [🇦🇺 Australian English](documentation/languages/README_en_AU.md)
* [🇯🇵 Japanese](documentation/languages/README_ja_JP.md) | [🇰🇷 Korean](documentation/languages/README_ko_KR.md) | [🇨🇳 Chinese (Simplified)](documentation/languages/README_zh_CN.md) | [🇹🇼 Chinese (Traditional)](documentation/languages/README_zh_TW.md)
* [🇮🇳 Hindi](documentation/languages/README_hi_IN.md) | [🇧🇩 Bengali](documentation/languages/README_bn_IN.md)
* [🇩🇪 German](documentation/languages/README_de_DE.md) | [🇫🇷 French](documentation/languages/README_fr_FR.md) | [🇪🇸 Spanish](documentation/languages/README_es_ES.md)
* [🇷🇺 Russian](documentation/languages/README_ru_RU.md) | [🇵🇱 Polish](documentation/languages/README_pl_PL.md) | [🇫🇮 Finnish](documentation/languages/README_fi_FI.md) | [🇸🇰 Slovak](documentation/languages/README_sk_SK.md)
* [🇸🇦 Arabic](documentation/languages/README_ar_SA.md)

## ⚙️ Global Installation

We provide a standalone, cross-platform binary installer featuring a robust Terminal User Interface (TUI). This single executable can automatically download the repository, install dependencies, configure Google Docs OAuth, and globally link your rules and skills to your AI agent.

### 🚀 Primary Installation (Recommended)
1. Download the latest `ai_installer` executable (Windows, macOS, Linux, `.deb`, `.rpm`) from the **[GitHub Releases](https://github.com/howlcipher/ai_knowledge_library/releases)** page.
2. Run the executable in your terminal:
   ```bash
   ./ai_installer
   ```

*The installer includes native options to **Install**, **Sync/Update**, or **Uninstall** the library.*

<details>
<summary><strong>Alternative Fallbacks (Non-Interactive)</strong></summary>
<br>

If you prefer not to use the compiled Go binaries, you can run the legacy setup scripts from within a cloned repository.

**Linux or macOS:**
```bash
chmod +x scripts/install_global.sh
./scripts/install_global.sh
```

**Windows:**
```powershell
.\scripts\install_global.ps1
```
</details>

***

## 📖 User Guide & Wiki

Once you have installed the library, what's next? We have prepared a comprehensive **[User Wiki & Guide](documentation/USER_GUIDE.md)** that explains:
* How to use the `ai_installer` control panel.
* How to launch the Multi-LLM Terminal UI or Web RAG interfaces.
* How to execute the embedded developer tools.
* How to utilize the local CI/CD regression guard.

***

## 🏗️ Architecture and Structure

The knowledge base is organized into specific domains that the AI agent natively understands and executes against.

| Directory or File | Primary Function |
| :--- | :--- |
| `GEMINI.md` | Global index and central rulebook for all agent interactions. |
| [`.agents/skills/`](.agents/skills/README.md) | The **AI Skills Library**. Domain-specific behavioral instructions parsed natively. |
| `.agents/rules/` | Global constraints that actively shape system prompts. |
| `scripts/` | Utilities for syncing and bootstrapping environments globally. |
| `projects/` | Active personal development projects and boilerplate templates. |
| `infrastructure/` | Networking setups, Docker configs, and server details. |
| `documentation/` | Standardized workflows, guides, and homelab postmortems. |
| `tools/` | Advanced tooling including ChromaDB vector indexers and Google Docs APIs. |
| `Makefile` | Standardized root entrypoints for testing, linting, and building. |

***

## 🔒 Security and Automation

This repository relies on several automated workflows to maintain structure and protect data autonomously:

* **GoReleaser CI/CD:** Fully automated release pipelines for cross-platform binary distribution.
* **Automated Test Suite:** Multi-language (Go and Python) testing matrix enforced on every push.
* **Vector Semantic Search:** Local ChromaDB integration (`src/infrastructure/build_vector_index.py`) for offline, secure RAG capabilities.
* **Adversarial & Negative Testing:** Automated prompt-injection safety suites (`src/core/adversarial_tester.py`) enforced on the LLM ruleset.
* **Google Docs Sync:** Authenticated OAuth integrations (`scripts/push_to_docs.py`) securely bridged to the local environment.
* **Markdown Validation:** GitHub Actions workflow that ensures all documentation adheres strictly to required formatting constraints.
* **Dependabot:** Automatically scans all connected Python and Go environments for known vulnerabilities weekly.

***

## 🧑‍💻 Forking and Customization

If you are forking this repository for your own use, you can easily customize the core user identity. Run the profile setup script to generate your own metadata while choosing to keep, supplement, or entirely replace the default William Elias profile.

```bash
python scripts/setup_profile.py
```

***

Please review the **[Change Log](change_log.md)** for a historical record of all updates and modifications.
