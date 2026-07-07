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
