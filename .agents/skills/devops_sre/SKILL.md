---
name: "devops_sre"
description: "Triggers when designing infrastructure-as-code (Terraform, Kubernetes) or building CI/CD pipelines (Azure DevOps, GitLab)."
---

# DevOps and Site Reliability Engineering Standards

This skill defines the mandatory architectural and operational standards for building infrastructure, automation pipelines, and software deployments. All infrastructure must be treated as code, remain highly maintainable, and be designed for zero-downtime operations and security.

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

## CI/CD Pipelines

When authoring or modifying continuous integration and continuous deployment pipelines:

1. **Pipeline as Code**: Write all pipelines in declarative formats (YAML) and version-control them alongside the application code. Avoid UI-configured build steps.
2. **Pipeline Reusability**: Implement shared, parameterized templates for common tasks (e.g., testing, building, and publishing) to eliminate duplication.
3. **Automated Gates and Security Analysis**: Enforce linting, formatting checks, unit tests, and integration tests on every commit. Integrate static application security testing (SAST), software composition analysis (SCA), and secret detection scanners in the pipeline. Fail builds if violations are detected.
4. **Zero-Downtime Strategy**: Enforce safe deployment patterns (canary, blue-green, or rolling updates) with automated regression verification.
5. **Environment Isolation**: Segment pipeline runners and environments cleanly. Require multi-party manual approval gates for production deployments. Maintain parity across development, staging, and production environments, injecting environment-specific variables at runtime.

## Network Engineering and Infrastructure Security

When designing SRE environment networks and deployment infrastructures:

1. **Network Segmentation**: Enforce strict micro-segmentation guidelines across all network zones (e.g., DMZ, internal, management) to restrict lateral movement.
2. **Default-Deny Policy**: Apply a default-deny policy on all firewalls and routers, explicitly permitting only authorized protocols, ports, and IP ranges.
3. **Network Automation**: Automate the generation, verification, deployment, and backup of switch and router configurations (IaC), storing them in version-controlled repositories.
4. **Redundancy and Failover**: Define and test redundant, dynamic routing protocols (e.g., OSPF, BGP) and fallback paths to guarantee high availability for critical resources.

## Reliability, Monitoring, and Incident Response

- **Log Centralization**: Enforce structured, centralized logging across all applications and infrastructure tools. Settle on a structured log format (e.g., JSON) and integrate system logs with a Security Information and Event Management (SIEM) pipeline.
- **Telemetry and Monitoring**: Continuously poll and log packet flows (NetFlow/IPFIX), interface statistics, and hardware telemetry to detect performance degradation or security anomalies.
- **Idempotency**: Enforce idempotency across all deployment, maintenance, and utility scripts. Multiple runs of a script must result in the same safe system state without side effects.
- **Automated Rollbacks**: Implement automated monitoring and rollback mechanisms that revert deployments immediately if error rates, latency, or system health metrics exceed defined thresholds post-deployment.
