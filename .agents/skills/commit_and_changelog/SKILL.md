---
name: "commit_and_changelog"
description: "Triggers during git staging reviews, workspace checkins, or summary generation"
---

# Workspace History Standards

This skill governs the conventions for reviewing workspace changes, writing git commits, and generating changelogs to ensure readable project history.

## Git Commit Conventions

### 1. Differential Analysis and Scoping
- Analyze staged repository diffs thoroughly to isolate the specific application modules or files that have been modified.
- Categorize changes according to standard scopes (e.g., `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`).

### 2. Formatting Rules
- Never use dashes as dividers in commit summaries or subjects.
- Use colons and spaces to separate the change scope from the descriptive commit message:
  - Format: `<type>(<scope>): <short description>` (e.g., `refine(tracker): update status for accessibility`).

## Changelog and Summary Standards

### 1. Change Summarization
- Provide a clean, high-level text summary of changes at the top of any generated changelog or documentation.
- Prioritize logical impact over a line-by-line code description.
- Use lists to group modifications by functional area (e.g., Added, Changed, Fixed, Removed).