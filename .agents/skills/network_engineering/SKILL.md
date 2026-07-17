---
name: "network_engineering"
description: "Triggers during network design, configuration, and monitoring tasks."
---

# Network Engineering Standards

Standards and protocols for designing, configuring, monitoring, and securing network infrastructure.

## Infrastructure and Segmentation
* **Network Segmentation**: Enforce strict micro-segmentation guidelines across all network zones (e.g., DMZ, internal, management) to restrict lateral movement and contain potential breaches.
* **Access Control Lists (ACLs)**: Enforce a default-deny policy on all firewalls and routers, explicitly permitting only authorized protocols, ports, and IP ranges.
* **Device Hardening**: Apply industry-standard security hardening benchmarks (such as CIS benchmarks) to all network devices. Disable unused services, configure secure SSH, and restrict management access.

## Configuration and Automation
* **Configuration Management**: Automate the generation, verification, deployment, and backup of switch and router configurations. Avoid manual configurations in production.
* **Version Control**: Store all network infrastructure configurations (Infrastructure as Code) in version-controlled repositories.
* **Automated CI/CD Gates**: Enforce automated syntax validation, linting, and security scanning on all network configurations prior to deployment.
* **Idempotent Deployments**: Ensure all configuration scripts are idempotent, yielding the same safe system state on repeated execution. Use zero-downtime deployment strategies (like rolling changes) with automated rollbacks when post-change verification fails.

## Operations and Resilience
* **Telemetry and Monitoring**: Continuous polling and logging of packet flows (NetFlow/IPFIX), interface statistics, and hardware telemetry to detect performance degradation or security anomalies.
* **Redundancy and Failover**: Define and test redundant, dynamic routing protocols (e.g., OSPF, BGP) and fallback paths to guarantee high availability for critical resources.
* **Lifecycle and Patching**: Automate and schedule routine firmware upgrades and patch management for network hardware within designated maintenance windows.
* **Backup Verification**: Maintain automated backup schedules for all network configuration states and perform regular recovery drills to guarantee Recovery Point Objectives (RPO) and Recovery Time Objectives (RTO).

## Security and Identity Governance
* **Access Governance**: Enforce the principle of least privilege. Require multi-factor authentication (MFA) and secure identity providers for all administrator logins and remote sessions.
* **Auditing and SIEM**: Enable centralized auditing and structured logging for all administrative commands, login attempts, and policy changes. Integrate these logs directly with a Security Information and Event Management (SIEM) pipeline.
