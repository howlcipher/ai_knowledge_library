---
name: "automation"
description: "Triggers during scripting, task scheduling, and repetitive workflow optimization"
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

## Infrastructure and Deployment Automation

### 1. Declarative Infrastructure-as-Code
- Define all infrastructure and provisioning tasks using declarative IaC tools (e.g., Terraform, Ansible). Avoid interactive script-based provisioning ("click-ops").
- Run automated syntax validation, linting (e.g., `tflint`), and security scanning (e.g., `tfsec`, `checkov`) on all declarative configurations prior to execution.

### 2. Secure Containerized Execution
- Build automation scripts running inside containers using minimal, trusted base images (e.g., distroless, Alpine Linux) to minimize the attack surface.
- Run containers as non-root users, set root filesystems to read-only, and limit container runtime capabilities.

### 3. Automated System Maintenance and Backups
- Automate OS patching, kernel upgrades, and packages during defined maintenance windows to minimize system downtime.
- Implement automated backup schedules for critical configurations and data, and schedule regular restoration drills to programmatically verify Recovery Point Objectives (RPO) and Recovery Time Objectives (RTO).
