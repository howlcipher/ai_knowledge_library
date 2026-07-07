# Change Log

All notable changes to this project will be documented in this file.

## 2026_07_07
* Created `change_log.md` and linked it in `README.md`.
* Created a standard Homelab Postmortem template in the `documentation` directory to track outages and issues.
* Created a Python script `github_profile_sync.py` in the `tools` directory to automatically fetch public GitHub repositories and keep the user profile updated.
* Created `infrastructure/network_diagram.md` containing personal homelab architecture.
* Created `tools/server_health_check.py` to monitor local system resources.
* Added GitHub Actions workflow for Markdown validation.
* Added Dependabot configuration for security vulnerability scanning on Python and Go dependencies.
* Built boilerplate templates for Python FastAPI and Go backend services inside `projects/templates/`.
* Created AGY formatting rule in `.agents/rules/strict_formatting.md` to automate constraints.
* Created `scripts/install_global.sh` to symlink library skills and rules globally for any AGY instance.
* Removed phone number from `USER_PROFILE.md` to protect Personally Identifiable Information.
* Removed phone number from `USER_PROFILE.md` to protect Personally Identifiable Information.
* Added `no_pii.md` global AGY rule and updated the `cyber_security` skill to strictly forbid handling sensitive PII like phone numbers.
* Created `scripts/install_global.ps1` to allow Windows users to sync skills and rules globally using PowerShell Junctions and Hard Links.
* Created `scripts/setup_profile.py` to allow individuals forking this repository to easily generate and swap in their own user profiles.
* Filled `improvements.md` with new automation tasks.
* Created `tools/sync_context.py` to map out local markdown files into a master index.
* Created `tools/fetch_security_news.py` to automatically update local docs with current cybersecurity threats.
* Created `tools/generate_agent_summary.py` to inject condensed profile data directly into the agent rules.
* Created `tools/clean_logs.py` to automate infrastructure maintenance by dropping old health records.
* Updated `GEMINI.md` to officially broaden language preferences to include Bash, while strictly requiring the right tool for the job.
* Added a global AGY rule in `.agents/rules/architecture.md` mandating pros and cons evaluations before committing to any architectural or infrastructure decisions.
* Built `tools/split_large_markdown.py` to automatically chunk large text files into 500 line segments, drastically improving AI reading speed and accuracy.
* Built `tools/scaffold_project.py` to rapidly generate production ready project structures for Python and Go.
* Created strict AGY rules in `.agents/rules/` to natively enforce Test Driven Development and automated code quality self reviews.
* Established an Architecture Decision Records structure at `documentation/adr/` and logged the first architectural decision.
* Deployed secure, ready to use Docker Compose templates inside `infrastructure/templates/`.
* Added `.agents/rules/documentation_enforcement.md` to guarantee the AI always updates the changelog and README prior to any git push.
* Cleared completed tasks from `improvements.md` and added new spawned tasks for cron scheduling and Git hook integration.
* Created `scripts/setup_cron.py` to seamlessly install the security news fetcher and log cleaner directly into the system crontab.
* Created `scripts/install_git_hooks.py` to bind the context synchronization tool to all future code commits automatically.
* Upgraded `tools/generate_agent_summary.py` to dynamically fetch live GitHub statistics via API to enrich the global system prompt.
* Cleared `improvements.md` and added three new spawned automation tasks.
* Executed Set 1: Implemented cron monitoring, advanced Git hooks, and multi source RSS aggregation.
* Executed Set 2: Created system health HTML dashboards, Prometheus Docker templates, and native AGY zero trust rules.
* Executed Set 3: Deployed automated library tarball backups, automated backup crons, and logged the Automation ADR.
* Executed Set 4: Developed backup retention sweepers, native Conventional Commits rules, and library statistics generators.
* Fully cleared the `improvements.md` backlog as all 4 conceptual sets were successfully implemented in bulk.
* Added `.agents/skills/bug_bounty_hunter/SKILL.md` to establish strict methodologies for reconnaissance, safe exploitation, and professional vulnerability reporting.
* Implemented Secrets Management Architecture by creating a strict AGY rule preventing hardcoded credentials.
* Built `tools/brain.py` to allow offline CLI searching of the entire knowledge base.
* Established `documentation/agent_memory/` for long term AI persistent memory retention.
* Created `tools/generate_knowledge_graph.py` to automatically visualize directory structures via Mermaid diagrams.
* Wrote `CONTRIBUTING.md` to officially guide external collaborators on formatting constraints.
* Built `documentation/roadmaps/2026_goals.md` to track technical and academic milestones.
* Added a new 'Purpose and Value' section to the README to clearly explain the project scope and why developers should adopt it.
* Executed a full repository validation sweep confirming zero dead links and zero empty directories across the entire knowledge base.
* Populated `improvements.md` with 4 new advanced infrastructure and testing automation tasks.
