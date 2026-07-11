# Global Coding Standards and Hygiene

This document defines the baseline coding hygiene, architectural patterns, and defensive programming practices that all agents (and humans) must follow when contributing to the codebase. 

Because this repository utilizes AI Orchestration, maintaining deterministic, extremely readable, and strictly typed code is vital to prevent context drift and hallucination.

## 1. Defensive Programming & Safety First
* **Fail Fast & Loudly**: Never swallow exceptions silently using `pass` or empty `catch` blocks. If an error occurs, log it explicitly with full context and halt execution if the system cannot recover safely.
* **Input Validation (Zero Trust)**: All external inputs—whether from an API, a file, a user, or another AI agent—must be strictly typed, validated, and sanitized at the exact boundary where they enter the system.
* **Immutability**: Prefer immutable data structures. When passing data between functions or modules, do not mutate objects in-place unless absolutely necessary for performance constraints.

## 2. Strong Typing and Self-Documenting Code
* **Explicit Types**: Use type hints universally (e.g., Python's `typing` module, Go's static typing, TypeScript). The goal is for the orchestrator/agent to read the signature and understand the IO without reading the function body.
* **Descriptive Naming**: Variables should describe their exact state. Avoid generic names like `data`, `item`, or `result`. Use names like `sanitized_context`, `raw_mcp_response`, or `is_qa_approved`.
* **Docstrings**: Every class and public method must have a docstring that briefly explains *what* it does, the arguments it takes, and what it returns. Avoid writing docstrings that just repeat the function name.

## 3. Architecture & Modularity
* **Single Responsibility Principle (SRP)**: A module or function should do exactly one thing. If a function is handling database fetching, sanitization, and UI rendering, it must be broken apart.
* **Dependency Injection**: Avoid hardcoding configurations or database connections deep inside utility functions. Pass them in as arguments or initialize them at the class level so code remains highly testable.
* **Statelessness Where Possible**: Avoid relying on global variables. State should be explicitly passed through the orchestration graph or stored in a dedicated persistent memory backend (like Chroma/Redis).

## 4. Security & Environment Constraints
* **No Hardcoded Secrets**: Passwords, API keys, and connection strings must never be hardcoded. They must be loaded dynamically via environment variables (`.env`) or a secrets manager.
* **Path Traversal Safety**: Any code that reads from or writes to the filesystem must validate that the target path does not traverse out of the intended sandbox directory.
* **Sandboxed Execution**: Subprocesses (like `subprocess.run` or `execute_bash_command`) must never execute raw un-sanitized string concatenations. 

## 5. Agentic AI Interactions (Specific to this Repo)
* **Context Efficiency**: Keep code DRY (Don't Repeat Yourself), but do not abstract things so deeply that an AI model requires opening 10 files to understand a simple execution flow. Balance DRY with locality of behavior.
* **Predictable Outputs**: When an AI agent is expected to parse output, ensure the output is structured (JSON, strictly formatted markdown, or predictable delimiters like `--- BEGIN ---`).

> **Enforcement:** The QA Reviewer Agent is instructed to enforce these rules on all generated code during the orchestration loop.
