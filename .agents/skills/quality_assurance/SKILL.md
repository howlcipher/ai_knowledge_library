---
name: "quality_assurance"
description: "Triggers during testing, validation, and QA processes."
---

# Quality Assurance Guidelines

Standards, methodologies, and guidelines for testing, validation, and quality assurance processes.

## Testing Principles and Isolation
* **Test Automation**: Prioritize automated test execution over manual verification to ensure reproducible, fast, and consistent validation.
* **Unit Testing**: Design unit tests to be completely isolated, stateless, and fast. Avoid external dependencies, database queries, or network requests in unit tests.
* **Integration Testing**: Write comprehensive integration tests to verify API endpoints, database transactions, and component interactions under realistic scenarios.

## Enforcements and Metrics
* **Coverage Thresholds**: Enforce strict, non-negotiable test coverage thresholds (e.g., branch and line coverage) for all new code submissions.
* **Regression Testing**: Execute full regression test suites on every pull request to identify side-effects or regressions in existing functional paths.
