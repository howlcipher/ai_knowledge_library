# Global Coding Standards and Hygiene

This document defines the baseline coding hygiene, architectural patterns, and defensive programming practices for the AI Knowledge Library. Because this repository utilizes AI Orchestration, maintaining deterministic, incredibly readable, and strictly typed code is vital to prevent context drift and hallucination.

## 1. Architectural Paradigms & Patterns
* **Context-Driven Architecture**: Choose paradigms based on the context. Use **Object-Oriented Programming (OOP)** for stateful systems (like Orchestrators, Database Clients, and Agents). Use **Functional Programming (FP)** for data transformation pipelines (like data sanitization, vector math, and log parsing) to ensure pure, side-effect-free execution.
* **Modularity (Single Responsibility)**: A module, class, or function should do exactly one thing. If a function is handling database fetching, sanitization, and UI rendering, it must be broken apart.
* **Dependency Injection**: Pass dependencies (database connections, config objects) as arguments rather than instantiating them deep inside logic. This keeps code highly testable and decoupled.
* **Dynamic DRY (Don't Repeat Yourself)**: Shy away from hardcoding magic numbers, URLs, or file paths. Extract them into configuration files (`.env`, `yaml`) or centralized constant files. Use dynamic template rendering when assembling repetitive structures.

## 2. Code Comments & Documentation
* **The "Why", Not the "What"**: Code should be self-documenting through clear variable names. Comments should explain *why* a decision was made (e.g., "Workaround for an upstream API bug") rather than *what* the code is doing (e.g., "Incrementing counter by 1").
* **Docstrings**: Every class and public method must have a docstring that briefly explains what it does, the arguments it takes, and what it returns. Avoid writing docstrings that just repeat the function name. 
* **TODOs and FIXMEs**: Must include context or a ticket tracking number. Do not leave anonymous, open-ended TODOs.

## 3. Strong Typing and Self-Documenting Code
* **Explicit Types**: Use type hints universally (e.g., Python's `typing` module, Go's static typing, TypeScript interfaces). The goal is for the orchestrator/agent to read the signature and understand the IO without reading the function body.
* **Descriptive Naming**: Variables should describe their exact state. Avoid generic names like `data`, `item`, or `result`. Use names like `sanitized_context`, `raw_mcp_response`, or `is_qa_approved`.

## 4. Defensive Programming & Safety First
* **Fail Fast & Loudly**: Never swallow exceptions silently using `pass` or empty `catch` blocks. If an error occurs, log it explicitly with full context and halt execution if the system cannot recover safely.
* **Input Validation (Zero Trust)**: All external inputs—whether from an API, a file, a user, or another AI agent—must be strictly typed, validated, and sanitized at the exact boundary where they enter the system.
* **Immutability**: Prefer immutable data structures. When passing data between functions or modules, do not mutate objects in-place unless absolutely necessary for performance constraints.

## 5. Security & Environment Constraints
* **No Hardcoded Secrets**: Passwords, API keys, and connection strings must never be hardcoded. They must be loaded dynamically via environment variables (`.env`) or a secrets manager.
* **Path Traversal Safety**: Any code that reads from or writes to the filesystem must validate that the target path does not traverse out of the intended sandbox directory.
* **Sandboxed Execution**: Subprocesses (like `subprocess.run` or `execute_bash_command`) must never execute raw un-sanitized string concatenations. 

## 6. Testing, Logging, & Telemetry
* **Structured Logging**: Use structured logging (JSON) over raw print statements in production paths to enable automated telemetry tracking and observability.
* **Testability**: Write unit tests for all complex business logic. Because we use Dependency Injection, mocking database states should be trivial.

## 7. Agentic AI Interactions (Specific to this Repo)
* **Context Efficiency**: Keep code DRY, but do not abstract things so deeply that an AI model requires opening 10 files to understand a simple execution flow. Balance DRY with locality of behavior.
* **Predictable Outputs**: When an AI agent is expected to parse output, ensure the output is structured (JSON, strictly formatted markdown, or predictable delimiters like `--- BEGIN ---`).

> **Enforcement:** The QA Reviewer Agent is instructed to enforce these rules on all generated code during the orchestration loop.
