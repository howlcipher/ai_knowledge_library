---
name: "python"
description: "PEP 8 style enforcement and flake8 linting standards for Python code."
triggers:
  - "python"
  - "flake8"
  - "pep8"
  - "pep 8"
  - "lint"
  - "linting"
tier: 1
---

# Python Standards

This skill governs Python code style and linting so that code passes `flake8` on the first try, both locally and in CI.

## Style Baseline

- Follow PEP 8 as the default style: 4-space indentation, `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Two blank lines before and after top-level `def`/`class` statements (E302/E305); one blank line between methods inside a class.
- One statement per physical line — never combine a condition and its body with a colon (E701), e.g. `if x: return` must be split across two lines.
- At least two spaces before an inline comment, and the comment itself starts with `# ` (E261/E262).
- Remove unused imports and variables before committing (F401/F841) — do not leave them "just in case."

## Linting Workflow

- Before declaring any Python task complete, run the project's actual flake8 invocation (check `.github/workflows/*.yml` or a `Makefile`/`tox.ini` for the exact paths and `--extend-ignore` flags) rather than guessing defaults — CI configs commonly ignore a small set of codes (e.g. line length or trailing whitespace) that a bare `flake8 .` would still flag.
- Treat any non-zero flake8 exit code as a build failure, not a warning: fix the reported line, don't suppress it with `# noqa` unless the rule genuinely does not apply and the suppression is scoped to the single line.
- When a CI "lint" job fails, reproduce it locally with the same command the workflow runs before pushing a fix — don't guess at the fix from the error text alone.

## Related Skills
- Defer to `software_development` for general clean-code, modularity, and defensive-error-handling standards that apply across languages.
- Defer to `test_and_verify` for the broader verification workflow (tests + lint) before marking work done.
