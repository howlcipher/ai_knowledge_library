---
name: "devops"
description: "Triggers during CI/CD pipeline creation, containerization, and infrastructure deployment"
---

# DevOps Practices and Standards

This skill establishes the mandatory practices and security standards for continuous integration and continuous deployment (CI/CD) pipelines, containerization, infrastructure-as-code (IaC), and reliable operations.

## Infrastructure as Code (IaC)

- **Declarative Provisioning**: Define all infrastructure components using declarative IaC tools (e.g., Terraform, OpenTofu, Ansible). Manual provisioning or modification of infrastructure ("click-ops") is strictly prohibited.
- **Modularity and Structure**: Segment configurations into logical, reusable modules (compute, networking, database) to avoid monolithic setups. Standardize variables with strict types and validation in `variables.tf`, and minimize outputs in `outputs.tf` to protect sensitive data.
- **Static Analysis and Validation**: Run automated syntax validation, linting (e.g., `tflint`), and security scanning (e.g., `tfsec`, `checkov`) on all IaC configurations during the CI process.
- **State Management**: Securely store IaC state files in remote backends with state locking and encryption enabled. Never commit local state files (e.g., `terraform.tfstate`) to version control.
- **Least Privilege and Drift Control**: Grant minimal necessary permissions when generating IAM roles and service principals, avoiding wildcards (`*`). Use automated configuration management tools to prevent configuration drift.

## Kubernetes Manifests and Deployment

- **Declarative Manifests**: Define all Kubernetes workloads and configurations fully in declarative manifests or Helm charts. Avoid imperative CLI commands (e.g., `kubectl run`) for production resource management.
- **Resource Constraints**: Enforce explicit CPU and memory `requests` and `limits` for all containers to ensure predictability and prevent node starvation.
- **Probes and Self-Healing**: Define appropriate liveness and readiness probes for all microservices to enable self-healing and prevent routing traffic to unhealthy pods.
- **Pod Security and Secret Isolation**: Enforce non-root execution (`runAsNonRoot: true`), disable privilege escalation (`allowPrivilegeEscalation: false`), and restrict system capabilities. Separate config from secrets using ConfigMaps for parameters and dynamic Secrets for credentials, certificates, and keys.

## CI/CD Pipelines

- **Pipeline as Code**: Author all pipelines in declarative YAML formats version-controlled alongside application code. Do not use UI-configured build steps.
- **Automated Gates and Reusability**: Enforce linting, formatting checks, unit tests, and integration tests on every commit using parameterized, shared pipeline templates.
- **Security Analysis**: Integrate static application security testing (SAST), software composition analysis (SCA), and secret detection scanners in pipelines. Fail builds if violations are detected.
- **Zero-Downtime Deployments**: Enforce rolling updates, blue-green deployments, or canary releases with automated post-deployment validation.
- **Environment Isolation and Approval Gates**: Segment pipeline runners and environments cleanly. Require multi-party manual approval gates before triggering production deployments.
- **Automated Rollbacks**: Implement automated monitoring and rollback mechanisms that revert deployments immediately if post-deployment metrics (error rates, latency) exceed defined thresholds.

## Reliability and System Operations

- **Log Centralization and Auditing**: Enforce structured, centralized logging across all applications, pipelines, and scripts. Log all privileged commands and integrate system logs with a Security Information and Event Management (SIEM) pipeline.
- **Idempotency**: Enforce strict idempotency across all deployment, maintenance, and utility scripts. Multiple runs must result in the same safe system state without side effects.
- **Lifecycle and Capacity Management**: Schedule and automate kernel upgrades, system patching, and package updates during maintenance windows. Monitor CPU, memory, disk, and network utilization to alert on anomalies.
- **Backup and Recovery Verification**: Establish automated backup schedules for critical states and databases. Perform regular restoration drills to verify recovery point objectives (RPO) and recovery time objectives (RTO).
- **System Hardening**: Apply industry-standard hardening benchmarks (such as CIS benchmarks) by disabling unused services, configuring strict firewall policies, and securing SSH configurations.

## Environment Standardization

- **Config Separation**: Maintain absolute parity in build environments, dependency versions, and deployment configurations across development, staging, and production. Inject environment-specific parameters exclusively via runtime environment variables.
