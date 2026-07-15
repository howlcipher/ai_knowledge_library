# 🧠 AI Skills Library

This directory contains the core cognitive and methodological domain instructions parsed by Antigravity (AGY) and other AI agents. 

When the AI encounters a task related to a specific domain (e.g., writing a web application, analyzing financial data, or debugging networking issues), it will load the corresponding skill from this library to mathematically anchor its methodologies, frameworks, and logic to your exact specifications.

---

## 🛠️ Current Skills Directory

### Software & Engineering
* **`architectural_guardrails`**: Defines system architecture constraints to prevent sprawling or unsustainable designs.
* **`defensive_debugging`**: Methodologies for hunting bugs with a zero-trust, log-first approach.
* **`software_development`**: General code quality, language-agnostic standards, and TDD constraints.
* **`frontend_engineering`**: Strict paradigms for React/Vue, state management, and modern CSS frameworks.
* **`database_management`**: SQL/NoSQL schema design, normalization, and indexing standards.

### Infrastructure & Security
* **`cyber_security`**: Broad InfoSec principles, zero-trust policies, and threat modeling.
* **`bug_bounty_hunter`**: Offensive security recon methodologies and safe exploitation strategies.
* **`devops`**: CI/CD pipelines, containerization (Docker/K8s), and infrastructure as code.
* **`devops_sre`**: Strict methodologies for Terraform modules, Kubernetes manifests, and templating Azure DevOps / CI/CD pipelines to infrastructure-as-code standards.
* **`network_engineering`**: Subnetting, routing, firewall rules, and topology documentation.
* **`system_administration`**: Linux administration, shell scripting standards, and crontab management.
* **`environment_doctor`**: Strategies for bootstrapping and fixing broken local development environments.

### Data & Machine Learning
* **`data_analyst`**: Pandas data wrangling, Scikit-Learn pipelines, and statistical validation.
* **`machine_learning`**: Model training methodologies, feature engineering, and bias mitigation.

### Business & Finance
* **`product_management`**: Writing PRDs, scoping minimum viable products, and defining OKRs.
* **`economic_theory`**: Macro/micro economic models, supply and demand, and behavioral economics.
* **`financial_theory`**: Corporate finance, DCF modeling, and capital asset pricing models (CAPM).
* **`quantitative_finance`**: Algorithmic trading, backtesting logic, and stochastic calculus.

### Design & User Experience
* **`ui_ux`**: User-centric design, wireframing, and user journey mapping.
* **`visual_design`**: White space, typography, and visual hierarchy principles.
* **`color_theory`**: Contrast, harmony, and psychological impacts of color.
* **`accessibility`**: Strict adherence to WCAG, ARIA labels, and screen-reader compatibility.

### Documentation & Management
* **`commit_and_changelog`**: Conventional commit enforcement and automated changelog updates.
* **`google_docs_writer`**: Drafting professional literature while enforcing local `.env` privacy.
* **`technical_writing`**: Structuring ADRs (Architecture Decision Records), Mermaid diagrams, and API specs.
* **`quality_assurance`**: Test matrices, integration testing, and release validation.
* **`test_and_verify`**: Strict requirements for building unit tests before declaring task completion.
* **`automation`**: Scripts and bots to handle repetitive infrastructure tasks.
* **`hallucination_guardrails`**: Mechanisms to force the AI to verify claims against local data before outputting.

### Hobbies & Specialized
* **`baseball_analytics`**: Advanced sabermetrics, predictive modeling, and player performance evaluation.
* **`gaming`**: Game design theory, mechanic loops, and player psychology.

---

## 🏗️ How to Add a New Skill

You can create an infinite number of specialized skills for your AI agent to learn. The AI reads these files dynamically, meaning any newly created skill is immediately actionable.

To create a new skill:
1. **Create a Directory:** Make a new folder inside `.agents/skills/` using a descriptive, lowercase name (e.g., `quantum_computing`).
2. **Create a `SKILL.md` File:** Inside that new folder, create a file explicitly named `SKILL.md`.
3. **Write the Instructions:** Follow this format:

```markdown
---
name: your_skill_name
description: A 1-2 sentence description of what this skill does and when the AI should trigger it.
---

# Your Skill Name

Write your detailed instructions, constraints, and methodologies here. 
The AI will read this file when performing tasks related to this domain, 
so focus on *how* you want the AI to behave, rather than just facts.
```

**Tip:** When you create a new skill, be sure to ask the AI to update this `README.md` file so your index stays accurate!
