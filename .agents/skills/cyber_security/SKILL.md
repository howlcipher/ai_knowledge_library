---
name: "cyber_security"
description: "Triggers during security audits, credential scanning, and vulnerability assessments"
triggers:
  - "security"
  - "hardening"
  - "security audit"
  - "vulnerability"
  - "credentials"
  - "secrets"
  - "zero trust"
  - "encryption"
tier: 1
---

# Cyber Security Directives

This skill outlines the core policies, standards, and security protocols governing infrastructure access, data protection, and privacy compliance under a zero-trust model.

## Infrastructure and Security Posture

### 1. Zero-Trust Access Architecture
- Implement a Zero-Trust architecture across all internal and external communication channels.
- Enforce continuous authentication and authorization. Never trust by default, regardless of whether a request originates internally or externally.
- Apply the principle of least privilege (PoLP) to all user accounts, service accounts, and API access tokens.

### 2. Secret and Credential Management
- Utilize automated scanning tools to detect exposed credentials, private keys, API tokens, and personally identifiable information (PII) in all repositories prior to code merges.
- Regularly rotate all API keys, service account credentials, and passwords according to corporate security policies.
- Encrypt all sensitive data at rest (using AES-256 or equivalent) and in transit (using TLS 1.3 or equivalent).

### 3. Auditability and Logging
- Maintain comprehensive, tamper-evident audit logs for all administrative, configuration, and data access actions.
- Centralize log storage in a secure, monitored location with restricted write-once read-many (WORM) access.

## Privacy and Data Protection

### 1. PII Restrictions
- Do not store telephone numbers, physical addresses, government identification numbers, or financial account details in code repositories, configuration files, or public logs.
- Permit only professional names and corporate email addresses within project documentation and files where necessary for identification.

### 2. Sensitive Data Disposal
- Ensure secure disposal and sanitization of staging and development environments to prevent leakage of operational or customer data.

## Adversarial Simulation and Vulnerability Analysis
- Align security audits and vulnerability assessments with adversary simulation frameworks (e.g., MITRE ATT&CK TTPs) to identify architectural and trust boundary flaws.
- Scan for OWASP Top 10 vulnerabilities, access control failures, and build attack path models showing propagation risks.
- Enforce strict boundaries: obtain explicit authorization prior to scanning, restrict initial discovery to passive reconnaissance, and never generate weaponized exploit payloads.
- Apply defensive translation by immediately pivoting from vulnerability identification to mitigation documentation.

## Threat Detection and Incident Response
- Monitor telemetry from SIEM, IDS/IPS, and EDR systems to detect real-time anomalies and credential abuse.
- Adhere to the NIST Incident Response lifecycle (Preparation, Detection/Analysis, Containment/Eradication/Recovery, Post-Incident Activity) during breach situations.
- Perform vulnerability management using CVSS and EPSS risk matrices to prioritize patching schedules.
- Follow digital forensics best practices to collect and preserve evidence without compromising system stability.
