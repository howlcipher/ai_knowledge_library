---
name: "devops_sre"
description: "Triggers when designing infrastructure-as-code (Terraform, Kubernetes) or building CI/CD pipelines (Azure DevOps, GitLab)."
---

# DevOps & Site Reliability Engineering (SRE) Methodologies

This skill defines the strict architectural and operational standards for building infrastructure, automation pipelines, and deployments. As a DevOps Engineer/SRE, infrastructure must be treated as code, highly maintainable, and designed for zero-downtime migrations.

## 🏗️ Infrastructure as Code (IaC) - Terraform

When writing Terraform modules or configurations, adhere to the following principles:

1. **Modularity over Monoliths:** Never write massive, single-file Terraform configurations. Break infrastructure down into reusable modules (e.g., `modules/networking`, `modules/compute`).
2. **State Management:** Always assume remote state (e.g., AWS S3 + DynamoDB locking, or Azure Storage). Never commit `terraform.tfstate` to version control.
3. **Variable Standardization:** Use consistent naming conventions for variables (e.g., `environment`, `project_name`, `region`). Define strict types and validation rules in `variables.tf`.
4. **Least Privilege:** When generating IAM roles or service principals, grant only the exact permissions required. Avoid wildcards (`*`).
5. **Output Cleanliness:** Only expose necessary outputs in `outputs.tf` to avoid leaking sensitive ARNs, IDs, or configurations.

## 🚢 Kubernetes Manifests (K8s)

When scaffolding Kubernetes deployments, services, or Helm charts:

1. **Declarative Integrity:** All deployments must be fully declarative. Avoid imperative `kubectl run` commands in documentation or scripts unless specifically for one-off debugging.
2. **Resource Limits & Requests:** NEVER generate a Pod or Deployment without explicitly defining CPU and memory `requests` and `limits`. This prevents node starvation.
3. **Liveness and Readiness Probes:** All microservices must include proper health checks. Do not deploy services that cannot self-heal or signal their readiness to the load balancer.
4. **Security Contexts:** Enforce strict security contexts. Containers should not run as `root` (`runAsNonRoot: true`), and `allowPrivilegeEscalation` should be `false`.
5. **Configuration Management:** Hardcode nothing. Inject all environment variables via `ConfigMaps` and sensitive credentials via `Secrets` (or external secret operators like Azure KeyVault / HashiCorp Vault).

## 🔄 CI/CD Pipelines (Azure DevOps / GitHub Actions)

When templating or modifying continuous integration and continuous deployment pipelines:

1. **Pipeline as Code:** All pipelines must be written in YAML and version-controlled alongside the application code. No UI-based pipeline configurations.
2. **Templating and Reusability:** Build generalized, reusable pipeline templates (e.g., a standard Python test template, a standard Go build template) rather than duplicating logic across dozens of repositories.
3. **Security Auditing & Linting:** Every pipeline must contain an early stage for security scanning (e.g., Dependabot, Bandit, Gosec) and linting. Fail the build immediately if security thresholds are violated.
4. **Zero Downtime Deployments:** Deployments should utilize strategies like Blue/Green, Canary, or Rolling Updates to ensure absolutely zero downtime during cutovers.
5. **Environment Segregation:** Clearly define boundaries between `dev`, `stage`, and `prod`. Production deployments must require manual human-in-the-loop approval gates.

## 🛡️ Reliability and Incident Response

- **Log-First Debugging:** Ensure all infrastructure components emit structured, centralized logs. If writing a script to deploy or migrate resources, include robust exception handling and logging (e.g., using `system_logger.py`).
- **Idempotency:** All scripts (Bash, Python, PowerShell) used in infrastructure must be idempotent. Running the script multiple times should yield the same safe state without causing errors or duplicating resources.
