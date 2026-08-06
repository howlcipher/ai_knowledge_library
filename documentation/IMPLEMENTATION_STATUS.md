# Implementation Status

## Current-State Assessment
The repository currently functions as a hybrid Go/Python project. Go provides the `ai_installer` CLI (using Cobra), while Python drives the `src/core` logic, testing, and vector indexing. The orchestrator logic and provider interactions exist but are spread across experimental Python files, and there is no unified `ai` command. 

## Completed Blueprint Capabilities
- **Portable Project Manifest (`.ai-project.toml`) v1:** schema (`schemas/ai-project.schema.json`), capability vocabulary (`schemas/capability.schema.json`), Go parser and validator (`internal/project/manifest.go`) enforcing schema version, required fields, known capabilities, relative/non-escaping context paths, and argv-array (non-shell-string) commands. Backed by `internal/project/manifest_test.go`, `internal/project/examples_test.go`, and the Python schema-drift regression test `tests/test_manifest_schema_drift.py`.
- **Project root discovery:** `internal/project/discover.go` walks up from a start path to the nearest `.ai-project.toml` or `.git`, with cross-platform-flavored coverage in `internal/project/discover_test.go`.
- **`ai project validate` command:** `cmd/ai/project.go` discovers the project root, loads and validates the manifest, and reports specific errors on failure.
- **Manifest specification document:** `documentation/PROJECT_MANIFEST_SPEC.md`.

(Legacy implementations of provider routing exist in `ai_router`/`src/core` but are not yet migrated to the unified framework.)

## Partially Completed Capabilities
- **CLI Foundation:** The `ai` executable (`cmd/ai`) exists with the `project validate` subcommand; the `ai_installer` Cobra CLI remains a separate pattern reference. Most commands from blueprint section 6.1 (`adopt`, `route`, `run`, `status`, etc.) are not yet implemented.
- **Provider Routing:** Partial logic exists in Python but is not part of the unified gateway.

## Missing Capabilities
- `ai adopt`, `ai route`, `ai run`, and the remaining unified CLI surface from blueprint section 6.1.
- Unified provider gateway and health checks.
- Formal task and event schemas (capability schema is done; task/event/result/handoff schemas are not).
- Scoped context indexing.

## Technical Risks
- **Language Divergence:** Parsing manifests in Go for the CLI may require duplicated parsing logic in Python if Python components also need to read `.ai-project.toml`.
- **Dependency Bloat:** Adding TOML parsing to Go requires an external dependency, as the standard library does not support TOML. 
- **Overlapping Orchestration:** Existing Python scripts and the new framework may drift if not unified cleanly.

## Architectural Decisions Still Required
- **Shared Parsing:** How will Python access the `.ai-project.toml` data (e.g., Go binary outputs JSON for Python, or duplicate parsing)?
- **State Location:** Final cross-platform standard paths for SQLite state and runs.

## Ordered Implementation Backlog
1. Define formal task, event, result, and handoff schemas (capability vocabulary is done).
2. Establish state-directory policy.
3. Implement `ai adopt`.
4. Package router behind an interface.

## Current Active Milestone
**Portable Project Contract v1 — complete**

All deliverables landed:
- `.ai-project.toml` JSON schema and capability schema (`schemas/`).
- Project root discovery (`internal/project/discover.go`).
- Manifest parsing and validation (`internal/project/manifest.go`), including schema version, required fields, known capabilities, relative/non-escaping context paths, and argv-array (non-shell-string) commands.
- `ai project validate` command (`cmd/ai/project.go`).
- Example manifests (`examples/manifests/*.toml`), all passing validation.
- Manifest specification document (`documentation/PROJECT_MANIFEST_SPEC.md`).
- Go test coverage (`internal/project/manifest_test.go`, `internal/project/discover_test.go`, `internal/project/examples_test.go`) and a Python schema-drift regression test (`tests/test_manifest_schema_drift.py`) that keeps the JSON schemas and example manifests from silently diverging.

Next milestone per the ordered backlog above: formal task/event/result/handoff schemas (blueprint section 11), which unblock packaging the router behind a shared interface.
