---
name: "quality_assurance"
description: "Triggers during testing, validation, and QA processes."
---

# Quality Assurance Guidelines

Standards, methodologies, and guidelines for testing, validation, and quality assurance processes.

## Testing Principles and Isolation
* **Test Automation**: Prioritize automated test execution over manual verification to ensure reproducible, fast, and consistent validation. Enforce strict success thresholds, where any test failure, compiler warning, or linter error invalidates the task.
* **Verification of State**: Never trust subjective claims of correctness. Always prove correctness via objective execution and verification of tests, logs, and build statuses.
* **Unit Testing**: Design unit tests to be completely isolated, stateless, and fast. Avoid external dependencies, database queries, or network requests in unit tests.
* **Integration Testing**: Write comprehensive integration tests to verify API endpoints, database transactions, and component interactions under realistic scenarios.
* **Sandboxed Execution**: Run all validation steps in a secure, sandboxed environment. Ensure test executions do not make unauthorized external network requests or modify persistent system states outside workspace boundaries.

## Enforcements and Metrics
* **Coverage Thresholds**: Enforce strict, non-negotiable test coverage thresholds (e.g., branch and line coverage) for all new code submissions.
* **Regression Testing**: Execute full regression test suites on every pull request to identify side-effects or regressions in existing functional paths.
* **Test-Driven Modification**: Before implementing a feature or fixing a bug, locate or write tests that cover the affected code pathways. Ensure new code is tested under both success and edge/failure conditions.
* **Tool Discovery**: Inspect the project directory structure to automatically identify native testing frameworks, run tools, compilers, and linters (e.g., pytest, cargo test, go test, npm test).

## Diagnostic Integration and Remediation
* **Defensive Troubleshooting**: When tests fail, execute a structured diagnostic protocol: log analysis (inspecting stack traces for exact error details), state/input isolation, and root cause analysis.
* **Remediation and Safety**: Remediation code must follow the minimal-change principle, conform to official style guides (e.g., PEP 8, Effective Go), and never perform unrelated refactoring.
* **Defensive Design**: Ensure fixes implement strict input validation (boundaries, types, schemas at system boundaries) and catch exceptions gracefully without leaking raw stack traces or configuration secrets to end users.
