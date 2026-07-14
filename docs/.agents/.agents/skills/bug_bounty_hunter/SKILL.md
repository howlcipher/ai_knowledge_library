name: "bug_bounty_hunter"
description: "Triggers during bug bounty reconnaissance, vulnerability analysis, and report generation"

# Bug Bounty Hunting Methodologies

## Reconnaissance Rules
* Always begin with passive reconnaissance before executing active scans to minimize detection and noise.
* Map out the entire attack surface comprehensively, prioritizing subdomains, API endpoints, and hidden administrative directories.
* Pay special attention to historical data, deprecated endpoints, and exposed source code.

## Vulnerability Analysis
* Prioritize Business Logic flaws and authorization bypasses like Insecure Direct Object References over simple automated scanner outputs.
* Systematically check for Server Side Request Forgery, Cross Site Scripting, and injection vulnerabilities in all user input fields.
* Never execute destructive payloads. Always construct safe, benign payloads to definitively prove the vulnerability exists without corrupting backend databases.

## Reporting Standards
* Write all vulnerability reports using standard HackerOne or Bugcrowd documentation structures.
* Always include a concise description, highly specific reproduction instructions, a calculated severity score, and the exact business impact.
* Provide actionable, developer friendly remediation advice to ensure the patch is robust.
