---
name: "network_engineering"
description: "Triggers during network design, configuration, and monitoring tasks."
---

# Network Engineering Standards

Standards and protocols for designing, configuring, monitoring, and securing network infrastructure.

## Infrastructure and Segmentation
* **Network Segmentation**: Enforce strict micro-segmentation guidelines across all network zones (e.g., DMZ, internal, management) to restrict lateral movement and contain potential breaches.
* **Access Control Lists (ACLs)**: Enforce a default-deny policy on all firewalls and routers, explicitly permitting only authorized protocols, ports, and IP ranges.

## Configuration and Automation
* **Configuration Management**: Automate the generation, verification, deployment, and backup of switch and router configurations. Avoid manual configurations in production.
* **Version Control**: Store all network infrastructure configurations (Infrastructure as Code) in version-controlled repositories.

## Operations and Resilience
* **Telemetry and Monitoring**: Continuous polling and logging of packet flows (NetFlow/IPFIX), interface statistics, and hardware telemetry to detect performance degradation or security anomalies.
* **Redundancy and Failover**: Define and test redundant, dynamic routing protocols (e.g., OSPF, BGP) and fallback paths to guarantee high availability for critical resources.
