---
name: "automation"
description: "Triggers during scripting, task scheduling, and repetitive workflow optimization"
triggers:
  - "automation"
  - "scripting"
  - "cron"
  - "scheduled task"
  - "workflow"
tier: 1
---

# Automation Guidelines and Standards

This skill establishes best practices for writing scripts, scheduling tasks, and optimizing repetitive workflows to ensure reliability, observability, and compliance with modern DevOps and system administration standards.

## Scripting and Execution Standards

### 1. Fault Tolerance and Resilience
- Write automation scripts that handle unexpected failures gracefully (e.g., using try-catch blocks, retry mechanisms, and fallback logic).
- Implement exponential backoff for external API calls and network-dependent tasks.
- Integrate automated rollback triggers if the execution script's error rates or latency exceed defined thresholds post-deployment.

### 2. Observability and Monitoring
- Output structured logs (e.g., JSON or key-value pairs) from all background and scheduled jobs.
- Ensure log payloads contain execution status, timestamps, target systems, and any error trace details.
- Integrate script logging with centralized auditing and Security Information and Event Management (SIEM) systems.
- Monitor execution resource utilization (CPU, memory, disk, network I/O) to alert on resource exhaustion or execution anomalies.

### 3. Workflow Consolidation
- Consolidate repetitive manual tasks into single, well-documented command-line tools or unified automation scripts.
- Avoid fragmented scripts that require manual intervention or coordination.

### 4. Security, Credentials, and Parity
- Never hardcode service credentials, API tokens, or secrets within automation scripts.
- Enforce the principle of least privilege: configure scripts, API tokens, and runner agents with the minimum system and network access required.
- Maintain environment parity across development, staging, and production environments. Inject configuration parameters exclusively via runtime environment variables.

## Related Skills
- Defer to `devops_sre` for declarative infrastructure-as-code standards and to `devops` for pipeline integration.
- Defer to `system_administration` for OS maintenance windows, patching, and backup schedules.
- Defer to `cyber_security` for secret management and least privilege baselines.
