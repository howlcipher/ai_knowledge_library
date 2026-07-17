---
name: "devops"
description: "Triggers during CI/CD pipeline creation, containerization, and infrastructure deployment"
---

# DevOps Practices and Standards

This skill establishes the mandatory practices and security standards for continuous integration and continuous deployment (CI/CD) pipelines, containerization, and infrastructure-as-code (IaC).

## Infrastructure as Code

- **Declarative Provisioning**: Define all infrastructure components using declarative IaC tools (e.g., Terraform, OpenTofu, Ansible). Manual provisioning or modification of infrastructure ("click-ops") is strictly prohibited.
- **Static Analysis and Validation**: Run automated syntax validation, linting (e.g., `tflint`), and security scanning (e.g., `tfsec`, `checkov`) on all IaC configurations during the CI process.
- **State Management**: Securely store IaC state files in remote backends with state locking and encryption enabled.

## CI/CD Pipelines

- **Automated Gates**: Configure build pipelines to enforce linting, formatting checks, unit tests, and integration tests on every commit. Code changes must pass all gates before merge.
- **Zero-Downtime Deployments**: Design deployment pipelines to utilize safe strategies such as rolling updates, blue-green deployments, or canary releases to eliminate application downtime.
- **Automated Rollbacks**: Implement automated monitoring and rollback mechanisms that revert deployments immediately if error rates, latency, or system health metrics exceed defined thresholds post-deployment.

## Containerization and Security

- **Minimal Base Images**: Build container images using minimal, trusted base images (e.g., distroless, Alpine Linux) to minimize the attack surface.
- **Vulnerability Scanning**: Integrate container image scanners (e.g., Trivy, Grype) into the CI pipeline. Block any image containing high or critical vulnerabilities from being pushed to the container registry.
- **Runtime Security**: Configure container runtimes with the principle of least privilege: run containers as non-root users, set root filesystems to read-only, and limit container capabilities.

## Environment Standardization

- **Config Separation**: Maintain absolute parity in build environments, dependency versions, and deployment configurations across development, staging, and production. Inject environment-specific parameters exclusively via runtime environment variables.
