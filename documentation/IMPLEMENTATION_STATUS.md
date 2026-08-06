# Implementation Status

## Current-State Assessment
The repository currently functions as a hybrid Go/Python project. Go provides the `ai_installer` CLI (using Cobra), while Python drives the `src/core` logic, testing, and vector indexing. The orchestrator logic and provider interactions exist but are spread across experimental Python files, and there is no unified `ai` command. 

## Completed Blueprint Capabilities
*None yet under the new framework structure.*
(Legacy implementations of provider routing exist in `ai_router`/`src/core` but are not yet migrated to the unified framework.)

## Partially Completed Capabilities
- **CLI Foundation:** The `ai_installer` demonstrates a Cobra-based Go CLI, which serves as a pattern for the `ai` executable.
- **Provider Routing:** Partial logic exists in Python but is not part of the unified gateway.

## Missing Capabilities
- `ai` unified executable.
- Portable Project Manifest (`.ai-project.toml`) and validation.
- Unified provider gateway and health checks.
- Formal task, event, and capability schemas.
- Scoped context indexing.

## Technical Risks
- **Language Divergence:** Parsing manifests in Go for the CLI may require duplicated parsing logic in Python if Python components also need to read `.ai-project.toml`.
- **Dependency Bloat:** Adding TOML parsing to Go requires an external dependency, as the standard library does not support TOML. 
- **Overlapping Orchestration:** Existing Python scripts and the new framework may drift if not unified cleanly.

## Architectural Decisions Still Required
- **Shared Parsing:** How will Python access the `.ai-project.toml` data (e.g., Go binary outputs JSON for Python, or duplicate parsing)?
- **State Location:** Final cross-platform standard paths for SQLite state and runs.

## Ordered Implementation Backlog
1. **Portable Project Contract v1** (Active Milestone)
2. Define capability vocabulary and task schemas.
3. Establish state-directory policy.
4. Implement `ai adopt`.
5. Package router behind an interface.

## Current Active Milestone
**Portable Project Contract v1**
- Deliverables: `.ai-project.toml` schema, project root discovery, `ai project validate` command, example manifests.
