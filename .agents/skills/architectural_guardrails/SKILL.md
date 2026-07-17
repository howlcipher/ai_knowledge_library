---
name: "architectural_guardrails"
description: "Triggers during project initialization, layout mapping, or structural documentation routines"
---

# Global Architectural Standards

This skill governs global structural conventions, visual layout mapping, and execution resiliency requirements for software projects.

## Code and Structural Layout Standards

### 1. Naming and Punctuation Conventions
Maintain consistent character usage for files, variables, and documentation:
- Do not use hyphens, dashes, or subtraction symbols as punctuation or dividers unless grammatically correct or syntactically required.
- Use underscores (`_`) for file names, directories, and database fields to ensure cross-platform compatibility.
- Use spaces for standard text and documentation headers.

### 2. Data Presentation
- Present complex datasets, configurations, and comparison matrices using clean, standardized Markdown tables.
- Do not use raw text walls or poorly structured lists for multi-dimensional data.

### 3. Documentation Conciseness
- Keep all summaries, status updates, and architectural decisions extremely concise.
- Focus strictly on impact, constraints, and decisions without verbose filler text.

## Execution Resiliency and Error Handling

### 1. Asynchronous Execution logic
- Design all background processes, daemon tasks, and asynchronous routines with non-blocking execution logic.
- Implement explicit timeouts, worker pool limits, and liveness monitoring for all long-running tasks.

### 2. Structured Failure Reporting
- Every error handling routine must emit a structured log payload (e.g., JSON format).
- Include the exact failure vector, stack trace, timestamp, and contextual metadata to ensure zero-trust traceability.