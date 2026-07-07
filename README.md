<div align="center">
  <img src="https://img.shields.io/static/v1?label=AI&message=Knowledge_Library&color=blueviolet&style=for_the_badge" alt="AI Library Badge" />
  <img src="https://img.shields.io/static/v1?label=Library_Size&message=235&color=success&style=for_the_badge" alt="Library Size Badge" />
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

## 🧠 Purpose and Value

**What it is:** A centralized, filesystem-based knowledge library and execution environment specifically engineered for AI agents operating within the terminal.

**Why use it:** AI agents frequently hallucinate or generate generic boilerplate when operating blindly. By linking this structured library to your local environment, you mathematically force the AI to:
* Inherit your specific engineering methodologies.
* Execute tasks using strictly defined domain skills.
* Automatically generate scaffolding, monitor infrastructure, and perform self-reviews before committing code.

It transforms generic AI models into a personalized, highly disciplined engineering team that operates precisely the way you do.

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
* **Vector Semantic Search:** Local ChromaDB integration (`tools/build_vector_index.py`) for offline, secure RAG capabilities.
* **Google Docs Sync:** Authenticated OAuth integrations (`tools/push_to_docs.py`) securely bridged to the local environment.
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