<div align="center">
  <img src="https://img.shields.io/static/v1?label=AI&message=Knowledge_Library&color=blueviolet&style=for_the_badge" alt="AI Library Badge" />
  <img src="https://img.shields.io/static/v1?label=Powered_By&message=Antigravity&color=blue&style=for_the_badge&logo=google" alt="Antigravity Badge" />
</div>

<h1 align="center">Personal AI Knowledge Library</h1>

<p align="center">
  <img src="https://img.shields.io/static/v1?label=Language&message=Python&color=3776AB&style=flat_square&logo=python" alt="Python Badge" />
  <img src="https://img.shields.io/static/v1?label=Language&message=Go&color=00ADD8&style=flat_square&logo=go" alt="Go Badge" />
  <img src="https://img.shields.io/static/v1?label=Platform&message=Docker&color=2496ED&style=flat_square&logo=docker" alt="Docker Badge" />
  <img src="https://img.shields.io/static/v1?label=OS&message=Linux&color=FCC624&style=flat_square&logo=linux" alt="Linux Badge" />
</p>

***

> This repository serves as the central context layer for terminal AI agents. It maps directly into the CLI to enforce coding standards, eliminate hallucinations, and provide deep architectural context tailored specifically for William Elias.

***

## Purpose and Value

**What it is:** A centralized, filesystem based knowledge library and execution environment specifically engineered for AI agents interacting within the terminal.

**Why use it:** AI agents frequently hallucinate or generate generic boilerplate when operating blindly. By linking this structured library to your local environment, you mathematically force the AI to:
* Inherit your specific engineering methodologies.
* Execute tasks using strictly defined domain skills.
* Automatically generate scaffolding, monitor infrastructure, and perform self reviews before committing code.

It transforms generic AI models into a personalized, highly disciplined engineering team that operates precisely the way you do.

***

## Architecture and Structure

The knowledge base is organized into specific domains that the AI agent natively understands and executes against.

<table>
  <tr>
    <th align="left">Directory or File</th>
    <th align="left">Primary Function</th>
  </tr>
  <tr>
    <td><code>GEMINI.md</code></td>
    <td>Global index and central rulebook for all agent interactions.</td>
  </tr>
  <tr>
    <td><code>.agents/skills/</code></td>
    <td>Domain specific behavioral instructions parsed natively by AGY.</td>
  </tr>
  <tr>
    <td><code>.agents/rules/</code></td>
    <td>Global constraints that actively shape system prompts.</td>
  </tr>
  <tr>
    <td><code>scripts/</code></td>
    <td>Utilities for syncing and bootstrapping environments globally.</td>
  </tr>
  <tr>
    <td><code>projects/</code></td>
    <td>Active personal development projects and boilerplate templates.</td>
  </tr>
  <tr>
    <td><code>infrastructure/</code></td>
    <td>Networking setups, Docker configs, and server details.</td>
  </tr>
  <tr>
    <td><code>documentation/</code></td>
    <td>Standardized workflows, guides, and homelab postmortems.</td>
  </tr>
  <tr>
    <td><code>tools/</code></td>
    <td>Automated scripts, health checks, and profile sync utilities.</td>
  </tr>
</table>

***

## Global Installation

We provide a standalone, cross-platform binary installer featuring a robust Terminal User Interface (TUI). This single executable can automatically download the repository, install Python dependencies, configure Google Docs OAuth, and globally link your rules and skills to AGY.

**Primary Installation (Recommended):**
1. Download the latest `ai_installer` executable (Windows, macOS, Linux, .deb, .rpm) from the **[GitHub Releases](https://github.com/howlcipher/ai_knowledge_library/releases)** page.
2. Run the executable in your terminal:
   ```bash
   ./ai_installer
   ```

*The installer will automatically clone the repository if you are running it externally, and includes native options to **Sync/Update** or **Uninstall** the library.*

**Alternative Fallbacks (Non-Interactive):**
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

***

## Forking and Customization

If you are forking this repository for your own use, you can easily customize the core user identity. Run the profile setup script to generate your own metadata while choosing to keep, supplement, or entirely replace the default William Elias profile.

```bash
python scripts/setup_profile.py
```

***

## Security and Automation

This repository relies on several automated workflows to maintain structure and protect data autonomously.

<details>
<summary><strong>View Automated Protections</strong></summary>
<br>

* **Markdown Validation**: GitHub Actions workflow that ensures all documentation adheres strictly to required formatting constraints.
* **Dependabot**: Automatically scans all connected Python and Go environments for known vulnerabilities weekly.
* **AGY Rule Engine**: Employs global rules to actively prevent the leakage of Personally Identifiable Information anywhere within terminal outputs.

</details>

***

Please review the [Change Log](change_log.md) for a historical record of all updates and modifications.