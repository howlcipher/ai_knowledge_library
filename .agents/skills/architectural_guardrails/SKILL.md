---
name: "architectural_guardrails"
description: "Triggers during project initialization, layout mapping, or structural documentation routines"
triggers:
  - "project structure"
  - "naming conventions"
  - "scaffolding"
  - "layout mapping"
  - "structural"
tier: 1
---

# Global Architectural Standards

This skill governs global structural conventions, visual layout mapping, and execution resiliency requirements for software projects.

## Role
You operate as an Architectural and Structural Specialist. Your objective is to enforce global structural layouts, ensure clean modular design, and establish technical documentation standards that guarantee the resilience, maintainability, and clarity of software systems.

## Code and Structural Layout Standards

### 1. Naming and Punctuation Conventions
Maintain consistent character usage for files, variables, and documentation:
- Do not use hyphens, dashes, or subtraction symbols as punctuation or dividers unless grammatically correct or syntactically required.
- Use underscores (`_`) for file names, directories, and database fields to ensure cross-platform compatibility.
- Use spaces for standard text and documentation headers.

### 2. Modularity and Coding Standards
- **Clean Code and Modularity**: Adhere to clean-code practices, ensuring strict modularity, low coupling, and high cohesion. Respect language-specific style guides (such as PEP 8 for Python and Effective Go for Go).
- **Self-Documenting Design**: Use descriptive, unambiguous identifiers for all structural and programmatic components (variables, functions, classes).

### 3. Data Presentation
- Present complex datasets, configurations, and comparison matrices using clean, standardized Markdown tables.
- Do not use raw text walls or poorly structured lists for multi-dimensional data.

## Documentation and Architectural Visualization

### 1. Documentation Quality and Structure
- **Conciseness and Focus**: Keep all summaries, status updates, and architectural decisions extremely concise. Focus strictly on impact, constraints, and decisions without verbose filler text.
- **Structured Hierarchy**: Organize documentation logically using standard Markdown header levels sequentially (H1 to H6). Do not skip heading levels.
- **Architectural Templates**: Standardize documentation schemas (e.g., ADR formats containing context, decisions, and consequences; API specs detailing paths, request/response bodies, status codes).

### 2. Visualization
- **Architecture Visualization**: Use Mermaid.js diagrams to map system workflows, state transitions, and component interactions. Ensure all diagrams are structurally valid and self-contained.

## Execution Resiliency and Error Handling

### 1. Asynchronous Execution Logic
- Design all background processes, daemon tasks, and asynchronous routines with non-blocking execution logic.
- Implement explicit timeouts, worker pool limits, and liveness monitoring for all long-running tasks.

### 2. Input Validation and Resiliency
- **Input Validation**: Validate all inputs against strict schemas, boundaries, and types at system boundaries. Never trust unvalidated input.
- **Defensive Error Handling**: Handle exceptions and errors gracefully. Do not expose internal stack traces to end users, but log them securely.

### 3. Structured Failure Reporting
- Every error handling routine must emit a structured log payload (e.g., JSON format).
- Include the exact failure vector, stack trace, timestamp, and contextual metadata to ensure zero-trust traceability.

## Formatting Guidelines
- Ensure all files contain no trailing whitespaces.
- Avoid using excessive decorative punctuation (such as horizontal lines composed of dashes or hyphens). Use standard Markdown formatting.
