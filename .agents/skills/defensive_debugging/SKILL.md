---
name: "defensive_debugging"
description: "Triggers during error troubleshooting, crash analysis, or runtime exception reviews"
tier: 1
---

# Defensive Debugging Standards

This skill defines the mandatory diagnostic protocol, isolation procedures, and validation requirements that must be executed when troubleshooting software errors, crash reports, or runtime exceptions.

## Diagnostic Protocol

Before modifying any source code or application configurations, execute the following sequential isolation process:

1. **Log Analysis**: Retrieve and thoroughly inspect the active application logs, stack traces, or terminal standard error (`stderr`) outputs. Identify the exact exception class, error code, and failure message.
2. **State and Input Isolation**: Isolate the specific source file, line number, and runtime state (including environment variables, configurations, database state, and user inputs) that triggered the execution block or crash.
3. **Root Cause Analysis**: Formulate and document a clear, evidence-based root cause explanation. Contrast what the system actually did with what it was expected to do, referencing specific lines of code or data.
4. **Remediation Design**: Devise a targeted fix that addresses the root cause directly. The fix must minimize the blast radius, adhere to the minimal-change principle, and avoid unrelated refactoring.

## Defensive Code Remediation Principles
- **Clean Code and Style Compliance**: Ensure all modifications adhere to the official style guides (e.g., PEP 8 for Python, Effective Go for Go) and clean-code practices. Use descriptive, self-documenting identifiers.
- **Input Validation**: When fixing input-triggered issues, implement strict validation mechanisms (boundaries, types, and schemas) at the system boundaries. Never trust incoming data.
- **Defensive Error Handling**: Always catch, handle, and log exceptions gracefully. Ensure the remediation prevents the leakage of internal system details, raw configuration parameters, or detailed stack traces to end users.
- **Least Privilege and Secure Defaults**: When debugging authorization or network connection failures, enforce least privilege execution and ensure cryptographically strong secure-by-default parameters.

## Verification and Regression Testing
- **Test Automation and Isolation**: Automate the verification of the fix. Write isolated, stateless, and fast unit tests to reproduce and verify the specific bug without relying on external databases or network queries.
- **Integration Testing**: For component interaction or state-dependent bugs, write integration tests that verify API endpoints, database transactions, and overall system workflow under realistic scenarios.
- **Coverage and Regression Suites**: Run regression tests on the affected code paths. Ensure the updated codebase complies with project test coverage thresholds (both line and branch coverage) and does not introduce side-effects.