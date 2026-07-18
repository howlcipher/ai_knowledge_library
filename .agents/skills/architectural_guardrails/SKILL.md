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

### 2. Data Presentation
- Present complex datasets, configurations, and comparison matrices using clean, standardized Markdown tables.
- Do not use raw text walls or poorly structured lists for multi-dimensional data.

### 1. Documentation Quality and Structure
- **Conciseness and Focus**: Keep all summaries, status updates, and architectural decisions extremely concise. Focus strictly on impact, constraints, and decisions without verbose filler text.
- **Structured Hierarchy**: Organize documentation logically using standard Markdown header levels sequentially (H1 to H6). Do not skip heading levels.
- **Architectural Templates**: Standardize documentation schemas (e.g., ADR formats containing context, decisions, and consequences; API specs detailing paths, request/response bodies, status codes).

### 2. Visualization
- **Architecture Visualization**: Use Mermaid.js diagrams to map system workflows, state transitions, and component interactions. Ensure all diagrams are structurally valid and self-contained.

## Execution Resiliency

### Asynchronous Execution Logic
- Design all background processes, daemon tasks, and asynchronous routines with non-blocking execution logic.
- Implement explicit timeouts, worker pool limits, and liveness monitoring for all long-running tasks.

## Formatting Guidelines
- Ensure all files contain no trailing whitespaces.
- Avoid using excessive decorative punctuation (such as horizontal lines composed of dashes or hyphens). Use standard Markdown formatting.

## Related Skills
- Defer to `software_development` for clean-code practice, defensive input validation, and structured failure reporting.
- Defer to `technical_writing` for documentation templates (ADRs, API specs) and Mermaid.js diagram standards.
