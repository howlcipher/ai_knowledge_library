---
name: "devops_sre"
description: "Triggers when designing infrastructure as code with Terraform, Kubernetes manifests, or Helm charts under site reliability engineering standards."
triggers:
  - "sre"
  - "terraform"
  - "kubernetes"
  - "helm"
  - "reliability"
  - "infrastructure as code"
tier: 2
---

# DevOps and Site Reliability Engineering Standards

This skill defines the mandatory architectural standards for designing infrastructure as code. All infrastructure must be treated as code, remain highly maintainable, and be designed for security, reliability, and zero-downtime operations.

## Infrastructure as Code with Terraform

When designing and writing Terraform configurations, adhere to the following principles:

1. **Modularity over Monoliths**: Avoid single-file or monolithic configurations. Segment infrastructure into logical, reusable modules (e.g., networking, compute, database).
2. **Remote State Management**: Store state files in remote backends (e.g., AWS S3, Azure Blob Storage) with state locking and encryption enabled. Never commit local state files (`terraform.tfstate`) to version control.
3. **Variable Standardization**: Enforce strict naming conventions for variables (e.g., `environment`, `project_name`, `region`). Define precise variable types and validation rules in `variables.tf`.
4. **Least Privilege Access**: Grant the minimal necessary permissions when generating Identity and Access Management (IAM) roles or service principals. Avoid wildcards (`*`) in policy statements.
5. **Output Integrity**: Expose only the minimum required output variables in `outputs.tf` to prevent the leakage of sensitive resource identifiers or connection strings.
6. **IaC Validation and Linting**: Integrate automated syntax validation, linting (e.g., `tflint`), and security scanning (e.g., `tfsec`, `checkov`) on all IaC configurations during the CI process.

## Kubernetes Manifests and Deployment

When scaffolding Kubernetes manifests, deployments, or Helm charts:

1. **Declarative Configuration**: Define resources fully in declarative manifests. Avoid imperative CLI commands (e.g., `kubectl run`) for production resource management.
2. **Resource Constraints**: Define explicit CPU and memory `requests` and `limits` for all containers to ensure resource predictability and prevent node starvation.
3. **Liveness and Readiness Probes**: Define proper liveness and readiness probes for all microservices to enable self-healing and prevent traffic routing to uninitialized or failing pods.
4. **Pod Security Contexts**: Enforce non-root execution (`runAsNonRoot: true`), disable privilege escalation (`allowPrivilegeEscalation: false`), and restrict system capabilities. Use minimal, trusted base images (e.g., distroless, Alpine) and integrate container image scanning (e.g., Trivy, Grype) into the CI pipeline.
5. **Configuration and Secret Isolation**: Separate application logic from environment configuration. Utilize ConfigMaps for configuration settings and dynamic Secrets for credentials, certificates, and keys.

## Related Skills
- Defer to `devops` for CI/CD pipeline standards, zero-downtime deployment strategies, and operational reliability.
- Defer to `network_engineering` for network segmentation, routing redundancy, and network telemetry.
- Defer to `cyber_security` for the secret management and least privilege baseline.
