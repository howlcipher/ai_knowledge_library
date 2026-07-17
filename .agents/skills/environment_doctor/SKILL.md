---
name: "environment_doctor"
description: "Triggers during sandbox checks, container monitoring, or runtime initialization"
---

# Environment Doctor Standards

This skill defines the operational standards and procedures for verifying, diagnosing, and restoring sandboxed development workspaces, runtime environments, and isolated containers.

## Runtime Isolation Verification

- **Isolation Integrity**: Inspect and verify that the active execution environment is properly isolated (e.g., inside a Docker container, virtual environment, or designated sandbox). Ensure that no unauthorized host-level directories are exposed.
- **Environment Drift Check**: Verify that crucial configuration parameters, environment variables (e.g., `PATH`, `PYTHONPATH`), and file permissions conform to the expected project specification.

## Dependency and Tool Auditing

- **Binary Auditing**: Regularly check the availability and execution status of vital system binaries, compilers, and database connections. Alert the user immediately if any tool is unresponsive or missing.
- **Version Gating**: Validate that the installed package versions (e.g., Python packages in `requirements.txt` or Node modules in `package.json`) strictly match the project's dependency lockfile.

## Diagnostics and Alerts

- **Failure Reporting**: Generate structured, detailed diagnostics when system errors or environment mismatches are detected. Specify the exact binary path, version conflict, or access error.
- **Remediation Protocols**: Provide the explicit bootstrap commands (e.g., `pip install -r requirements.txt`, `npm ci`, or `make bootstrap`) necessary to safely restore the sandbox or target environment to a clean, known-good operational state.