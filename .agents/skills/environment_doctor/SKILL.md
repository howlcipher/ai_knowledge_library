---
name: "environment_doctor"
description: "Triggers during sandbox checks, container monitoring, or runtime initialization"
tier: 1
---

# Environment Doctor Standards

This skill defines the operational standards and procedures for verifying, diagnosing, and restoring sandboxed development workspaces, runtime environments, and isolated containers.

## Runtime Isolation and Security Verification

- **Isolation Integrity**: Inspect and verify that the active execution environment is properly isolated (e.g., inside a Docker container, virtual environment, or designated sandbox). Ensure that no unauthorized host-level directories are exposed.
- **Environment Drift Check**: Verify that crucial configuration parameters, environment variables (e.g., `PATH`, `PYTHONPATH`), and file permissions conform to the expected project specification. Ensure strict environment parity across dev, staging, and production runtimes.
- **Least Privilege and Container Hardening**: Audit container runtimes to ensure they enforce non-root execution (`runAsNonRoot`), read-only root filesystems where possible, and run with the minimum capabilities required. Validate that container images have undergone vulnerability scans.

## Dependency, Tool, and Resource Auditing

- **Binary Auditing**: Regularly check the availability and execution status of vital system binaries, compilers, and database connections. Alert the user immediately if any tool is unresponsive or missing.
- **Version Gating**: Validate that the installed package versions (e.g., Python packages in `requirements.txt` or Node modules in `package.json`) strictly match the project's dependency lockfile.
- **Resource and Capacity Audits**: Monitor workspace and runtime resource utilization (such as disk usage, CPU, memory pressure, and file descriptor limits) to alert on performance anomalies.

## Diagnostics, Remediation, and Recovery

- **Failure Reporting**: Generate structured, detailed diagnostics (e.g., JSON format) when system errors or environment mismatches are detected. Specify the exact binary path, version conflict, error vectors, or access errors.
- **Idempotent Remediation Protocols**: Provide explicit, idempotent bootstrap commands (e.g., `pip install -r requirements.txt`, `npm ci`, or `make bootstrap`) necessary to safely restore the sandbox or target environment to a clean, known-good operational state. Remediation runs must be safe to execute repeatedly without side effects.
- **Backup and Recovery Audits**: Verify local state backup schedules, ensuring recovery processes meet targeted Recovery Point Objectives (RPO) and Recovery Time Objectives (RTO).
- **SIEM and Audit Integration**: Log all diagnostics, privilege escalations, and remediation executions to a centralized auditing system or SIEM pipeline for compliance tracking.