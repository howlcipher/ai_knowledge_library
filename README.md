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

To make this library accessible across your entire machine regardless of your current directory, run the provided setup scripts.

**For Linux or macOS users:**
```bash
chmod +x scripts/install_global.sh
./scripts/install_global.sh
```

**For Windows users:**
Execute the PowerShell installation script.
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