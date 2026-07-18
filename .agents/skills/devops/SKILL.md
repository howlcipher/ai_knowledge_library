---
name: "devops"
description: "Triggers during CI/CD pipeline creation, containerization, and infrastructure deployment"
triggers:
  - "ci/cd"
  - "pipeline"
  - "docker"
  - "container"
  - "deployment"
tier: 2
---

# DevOps Practices and Standards

This skill establishes the mandatory practices and security standards for continuous integration and continuous deployment (CI/CD) pipelines, containerization, infrastructure-as-code (IaC), and reliable operations.

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

## Environment Standardization

- **Config Separation**: Maintain absolute parity in build environments, dependency versions, and deployment configurations across development, staging, and production. Inject environment-specific parameters exclusively via runtime environment variables.

## Related Skills
- Defer to `devops_sre` for Terraform and Kubernetes design standards (modules, state, manifests, pod security).
- Defer to `system_administration` for OS lifecycle management, hardening benchmarks, and backup verification.
- Defer to `automation` for scripting standards behind pipeline and maintenance jobs.
