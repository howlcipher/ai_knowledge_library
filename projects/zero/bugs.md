# 🐛 Bug Backlog

This document is the authoritative, ranked backlog for known flaws, bugs, and broken items specifically for the Zero transpiler project. It mirrors the structure of `improvements.md` and follows the same Working Protocol.

## Ranked Backlog (best ROI first)

Pending bugs carry the same diminishing-returns score defined in `improvements.md` (Score = Value × Decay ÷ Effort). Bugs rarely decay, so Decay is normally 1.0.

| # | Bug | Status | Score (V×D÷E) | Claude model | Gemini model | ROI rationale |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [Lexer panics on EOF during unterminated string](#1-lexer-panics-on-eof-during-unterminated-string) | Done | 4.0 (4×1÷1) | Haiku 3 | Gemini 1.5 Flash | The lexer reports the error via `reportError`, but an explicit bounds check prevents potential runtime panics during deep parsing. |
| 2 | [Python Orchestrator timeout with heavy models](#2-python-orchestrator-timeout-with-heavy-models) | Done | 3.0 (3×1÷1) | Haiku 3 | Gemini 1.5 Flash | Added explicit UX warnings to console so users don't assume the script has frozen when loading heavy models in Outlines. |
| 3 | [Variable Shadowing in Go Generation](#3-variable-shadowing-in-go-generation) | Done | 4.0 (4×1÷1) | Sonnet 3.5 | Gemini 1.5 Pro | `let` expressions without inner `{}` brackets risk leaking scopes or redeclaring variables, causing Go compilation to fail on nested conditionals. |
| 4 | [Outlines EBNF Compilation Memory Limit](#4-outlines-ebnf-compilation-memory-limit) | Done | 2.5 (5×1÷2) | Sonnet 3.5 | Gemini 1.5 Pro | Optimized the CFG to only enforce generic S-expression balanced parentheses, avoiding OOM on massive state machines while deferring semantic validation to the Go transpiler. |
| 5 | [AST Deep Nesting Stack Limits](#5-ast-deep-nesting-stack-limits) | Done | 2.0 (4×1÷2) | Sonnet 3.5 | Gemini 1.5 Pro | Added an explicit depth parameter and limit of 1000 to `generateStatement` to fail gracefully with a JSON error instead of crashing the Go call stack. |
| 6 | [Include Paths Relative to File](#6-include-paths-relative-to-file) | Done (2026-07-22) | 6.0 (6×1÷1) | Sonnet 3.5 | Gemini 1.5 Pro | `(include "file.zero")` uses current working directory rather than resolving paths relative to the file doing the inclusion. |
| 7 | [defun Typing Rigidness](#7-defun-typing-rigidness) | Pending | 1.75 (7×1÷4) | Sonnet 3.5 | Gemini 1.5 Pro | All `defun` arguments strictly compile to Go `string` types, breaking if we try to pass an `*http.Request` or `int` to a function. |
| 8 | [try_let Error Interception Rigidness](#8-try_let-error-interception-rigidness) | Pending | 1.66 (5×1÷3) | Sonnet 3.5 | Gemini 1.5 Pro | `try_let` is currently hardcoded to only support `parse_json` as the error-returning function. Needs generalization. |
## Details

### 1. Lexer panics on EOF during unterminated string
In `zero.go`, the string lexer currently scans for the next quote. If EOF is hit, it correctly calls `reportError`, but if the file is truly truncated, we should ensure no other routines attempt to consume past the array bounds. The code is mostly safe but needs explicit unit tests to guarantee it never panics outside of the controlled JSON error output.

### 2. Python Orchestrator timeout with heavy models
When running `orchestrator.py` against a local Ollama instance with a large model (e.g. 70B parameters), the structured generation engine in `outlines` might hang for a long time compiling the regex/grammar. We need to add logging or a loading indicator so the user knows the compilation/generation hasn't silently frozen.

### 6. Include Paths Relative to File
* **Description:** `(include "file.zero")` uses `os.ReadFile(filename)`.
* **Why:** If the zero compiler is run from a different directory, it will fail to find relative included files.
* **Impact:** 6/10 (High).

### 7. defun Typing Rigidness
* **Description:** `defun` maps all arguments to strings in Go.
* **Why:** We cannot cleanly pass `req` to helper functions without using strings.
* **Impact:** 7/10 (High).

### 8. try_let Error Interception Rigidness
* **Description:** `try_let` only intercepts `parse_json` right now.
* **Why:** Needs to generalize to any function returning `(value, error)`.
* **Impact:** 5/10 (Medium).
