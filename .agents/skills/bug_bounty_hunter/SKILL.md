---
name: "bug_bounty_hunter"
description: "Triggers during bug bounty reconnaissance, vulnerability analysis, and report generation"
triggers:
  - "bug bounty"
  - "recon"
  - "disclosure"
  - "proof of concept"
  - "cvss"
tier: 2
---

# Bug Bounty Hunting Methodologies

This skill establishes structured procedures for target reconnaissance, systematic vulnerability analysis, and standard disclosure reporting under zero-trust, safe-harbor guidelines.

## Reconnaissance and Attack Surface Mapping

### 1. Passive Reconnaissance
- Always initiate target analysis with passive reconnaissance techniques and OSINT channels (e.g., DNS history, WHOIS, certificate transparency logs, search engine hacking) before executing active scans. This minimizes discovery noise and system impact while mapping the surface from an adversary's perspective (aligning with MITRE ATT&CK).

### 2. Comprehensive Surface Mapping
- Map the entire target attack surface systematically. Prioritize discovery of subdomains, API endpoints, parameters, and hidden administrative interfaces.
- Examine historical archives, deprecated endpoints, and exposed source code repositories for credentials, private keys, API tokens, or configuration leaks.

## Vulnerability Analysis and Exploitation Safety

### 1. Logic and Authorization Flaws
- Prioritize identifying Business Logic vulnerabilities, authorization bypasses (e.g., Insecure Direct Object References - IDOR), and authentication flaws over automated scanner outputs.
- Verify security assumptions on state transitions, multi-tenant boundaries, and input processing under Zero-Trust rules (continuous verification and least privilege).

### 2. Input and Protocol Validation
- Systematically check for Server-Side Request Forgery (SSRF), Cross-Site Scripting (XSS), SQL/NoSQL injections, and XML External Entity (XXE) vulnerabilities (covering the OWASP Top 10) in all user-supplied inputs and headers.
- Evaluate the feasibility of attack path modeling, showing how multiple low-impact vulnerabilities can be chained together to bypass defense-in-depth boundaries.

### 3. Safe Payload Design
- Never execute destructive payloads, denial of service exploits, or commands that modify backend systems.
- Construct benign proof-of-concept (PoC) payloads (e.g., executing `whoami` or reading non-sensitive system properties) to prove vulnerability existence without impacting system availability, performance, or data integrity.

## Vulnerability Reporting Standards

### 1. Report Structure
- Document all vulnerability disclosures using standard templates (e.g., HackerOne, Bugcrowd).
- Include the following mandatory sections: Summary, Vulnerable Component/Endpoint, Severity (using CVSS v3.1/v4.0), Detailed Proof of Concept, Business Impact, and Remediation.

### 2. Precision and Reproducibility
- Write precise, step-by-step reproduction instructions.
- Attach raw HTTP request/response logs, screenshot proof, or minimal exploit scripts to facilitate developer verification.

### 3. Actionable Remediation
- Provide specific, developer-friendly remediation guidance. Focus on structural fixes (e.g., parameterized queries, secure coding patterns) rather than superficial workarounds.
- Apply defensive translation, pivoting immediately from the vulnerability description to mitigation steps (e.g., least privilege, secure input handling, AES-256/TLS 1.3 encryption).

### 4. Privacy and PII Protection
- Apply the PII restrictions defined in `cyber_security`: redact personal identifiers and financial details from all proof-of-concept logs, reports, and screenshots.

## Related Skills
- Defer to `red_team` for adversary simulation methodology and engagement planning beyond bounty scope.
- Defer to `cyber_security` for the zero-trust and secret management baseline under test.
