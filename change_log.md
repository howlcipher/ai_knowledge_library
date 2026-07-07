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
