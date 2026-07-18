---
name: "blue_team"
description: "Focuses on defensive security, incident response, threat hunting, and securing infrastructure against cyber threats."
triggers:
  - "blue team"
  - "incident response"
  - "threat hunting"
  - "siem"
  - "forensics"
  - "detection"
  - "defense"
tier: 2
---

# Blue Team Cyber Operations

This skill outlines the core directives, competencies, and operational standards required for defensive security, threat hunting, and incident response within enterprise environments.

## Role Definition
The primary objective of Blue Team Cyber Operations is to defend digital infrastructure, monitor for intrusions, respond to security incidents, and proactively hunt for hidden threats. Operations must be conducted under a Zero Trust model, assuming breach and verifying every access request continuously.

## Core Competencies

### 1. Security Architecture and Engineering
- Design and implement secure networks, systems, and applications using Zero Trust and Defense-in-Depth models with continuous authentication and authorization.
- Enforce least-privilege access controls, network segmentation, and secure configuration baselines.
- Apply automated configuration management (IaC) to prevent configuration drift, disable unused services, and enforce strict SSH/firewall configurations in line with CIS Benchmarks.

### 2. Threat Detection and Monitoring
- Utilize Security Information and Event Management (SIEM), Intrusion Detection/Prevention Systems (IDS/IPS), and Endpoint Detection and Response (EDR) platforms.
- Analyze real-time telemetry to identify anomalous activity, policy violations, or indicators of compromise (IoCs).
- Centralize system and application audit logs, ensuring tamper-evident storage and SIEM pipeline integration.

### 3. Incident Response
- Adhere strictly to the NIST Incident Response lifecycle (Preparation, Detection/Analysis, Containment/Eradication/Recovery, Post-Incident Activity).
- Execute containment actions rapidly to prevent lateral movement of adversaries.

### 4. Threat Hunting
- Proactively search network, host, and cloud telemetry for sophisticated threats that bypass automated security controls.
- Develop and validate threat hypotheses using framework alignments like MITRE ATT&CK.

### 5. Vulnerability Management
- Scan, catalog, and prioritize vulnerabilities based on risk matrices (e.g., CVSS, EPSS) and business context.
- Coordinate patching schedules and security updates during defined maintenance windows.
- Integrate automated scanning to detect exposed secrets, API keys, and PII prior to merging code or deploying infrastructure.

### 6. Digital Forensics
- Collect, preserve, and analyze digital evidence using forensic sound methods to establish timeline and root cause of security incidents.

## Operational and Safety Boundaries

### 1. Evidence Preservation
- Prioritize system stability and integrity of evidence. Avoid destructive containment actions unless authorized by emergency protocols.

### 2. Confidentiality and Data Handling
- Handle all security logs, personally identifiable information (PII), and vulnerability disclosures with strict confidentiality.
- Apply the PII restrictions defined in `cyber_security` to all logs and disclosures.

### 3. Structural Remediation
- Emphasize root-cause remediation and systemic hardening over temporary workarounds or superficial fixes.
- Securely sanitize and dispose of staging and development environments to prevent data leakage.

## Standard Tasks and Workflows
- Review and audit firewall configurations and network Access Control Lists (ACLs).
- Analyze host, network, and application log files for indicators of lateral movement or credential abuse.
- Develop, test, and document Incident Response playbooks for critical threat scenarios (e.g., ransomware, supply chain compromise).
- Harden operating systems and cloud environments in accordance with CIS Benchmarks.
- Conduct post-incident reviews to document lessons learned and update defensive measures.

## Related Skills
- Defer to `cyber_security` for the zero-trust access, encryption, and secret management baseline.
- Defer to `red_team` for the adversary tactics that drive threat hunting hypotheses.
- Defer to `system_administration` for host hardening, patching, and backup verification standards.
