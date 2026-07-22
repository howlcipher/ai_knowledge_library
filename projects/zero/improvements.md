# 🚀 Improvement Backlog

This document is the authoritative, ranked backlog for the Zero transpiler project. It mirrors the format used in the main AI Knowledge Library.

## Working Protocol

This protocol applies to every worked task in the Zero project:

1. **Open a task journal.** Record your steps in a `YYYY-MM-DD_task_name.md` file if the task is complex.
2. **Re-evaluate the model.** Pick the least expensive available model (e.g., local Ollama, Claude, or Gemini) that can do the job well for the Zero transpiler.
3. **Route the crafted skills.** Check `.agents/skills/zero_transpiler/SKILL.md` before planning.
4. **Scan for helpful free tools.** Ensure you aren't rebuilding something already available.
5. **Finish the loop.** Every code change ships with relevant tests. Run Go builds (`go build`) and Python script validations before committing.

## Ranked Backlog (best ROI first)

Pending rows are ranked by a diminishing-returns score:

**Score = (Value × Decay) ÷ Effort**
- **Value (1–8):** pain or risk removed if the item ships.
- **Decay:** geometric halving per already-shipped item in the same theme (1.0 → 0.5 → 0.25 …).
- **Effort (1–8):** roughly log-scale; 1 = minutes, 8 = weeks.

| # | Improvement | Status | Score (V×D÷E) | Claude model | Gemini model | ROI rationale |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [Add Routing Support](#1-add-routing-support) | Done | 8.0 (8×1÷1) | Sonnet 3.5 | Gemini 1.5 Pro | Highest value to allow building web apps with multiple endpoints instead of just the root path. |
| 2 | [Add Conditionals and Variables](#2-add-conditionals-and-variables) | Pending | 4.0 (8×1÷2) | Sonnet 3.5 | Gemini 1.5 Pro | Necessary for basic logic flow in handlers (checking methods, parsing headers). |
| 3 | [Extend Python Orchestrator Grammar](#3-extend-python-orchestrator-grammar) | Pending | 4.0 (4×1÷1) | Haiku 3 | Gemini 1.5 Flash | Must update the grammar in `orchestrator.py` immediately after adding new Go AST features so the LLM can use them. |
| 4 | [Add Database Connections (SQL)](#4-add-database-connections-sql) | Pending | 3.0 (6×1÷2) | Sonnet 3.5 | Gemini 1.5 Pro | Crucial for dynamic data and actual web service capabilities. |
| 5 | [Add JSON Request/Response Handling](#5-add-json-requestresponse-handling) | Pending | 2.5 (5×1÷2) | Sonnet 3.5 | Gemini 1.5 Pro | Needed to build standard REST APIs. |

## Details

### 1. Add Routing Support
The transpiler currently hardcodes a single root `/` route in `http.HandleFunc`. We need to introduce a `(route "/path" (lambda ...))` expression in the AST to support standard web app architectures.

### 2. Add Conditionals and Variables
Introduce `let` and `if` blocks to handle internal request logic. For example: `(if (= req.method "POST") ...)`. This will require updating the Lexer to handle operators like `=` and the Code Generator to output Go `if` statements.

### 3. Extend Python Orchestrator Grammar
Currently, `orchestrator.py` uses a strict regex for the proof-of-concept single endpoint. As we implement improvements 1 and 2, this regex needs to be translated into a full Context Free Grammar (CFG) using Outlines to support nested expressions and arbitrary routes.

### 4. Add Database Connections (SQL)
Implement SQL database connections via Go's `database/sql` mapping to an S-expression like `(sql_query db "SELECT * FROM users")`.

### 5. Add JSON Request/Response Handling
Implement `(json_parse req.body)` and `(json_response data)` to easily map Go structs to JSON for API endpoints.
