---
name: howlframe-transpiler
description: Canonical HowlFrame language and transpiler guidance covering the compiler, .howl source, HFIR, bytecode, VM, backends, examples, fixtures, builds, tests, and verification. Use to write a HowlFrame program or change any of those toolchain components.
---

# HowlFrame Language and Toolchain

HowlFrame is an AI native programming language and verified execution platform for adaptive software. Its governing boundary is that intent is not authority: adaptive operations may reason and propose, while deterministic machinery owns capabilities, persistent state, irreversible mutations, invariants, verification, and approval.

This skill is the language specific operating reference. For the current implementation state, inspect the repository files named here instead of relying on remembered coverage.

## Canonical Identity

| Concept | Canonical value |
| --- | --- |
| Project | HowlFrame |
| Repository | `https://github.com/howlcipher/howlframe` |
| Go module | `github.com/howlcipher/howlframe` |
| Compiler source | `howlframe.go` |
| Compiler executable | `howlframe` |
| Source extension | `.howl` |
| Intermediate representation | HFIR, HowlFrame Intermediate Representation |
| Explicit bytecode extension | `.hfbc`, HowlFrame bytecode |
| Pages site | `https://howlcipher.github.io/howlframe/` |

Do not introduce compatibility aliases for an earlier project identity. Ordinary uses of the mathematical concept zero remain valid when they describe a value, length, index, or other nonbranding concept.

## Grounding Sources

Check these files before asserting that a construct or target is supported:

1. `README.md` for the current user facing toolchain and commands.
2. `internal/construct/` for authoritative standalone bytecode target coverage.
3. `internal/hfir/` for lowering, verification, target feasibility, and diagnostics.
4. `bugs.md` and `improvements.md` for current defects and roadmap status.
5. `docs/reference/bytecode_reference.md` and backend tests for artifact contracts.

Do not claim a roadmap feature is implemented merely because its syntax appears in a design document. Backend support differs by target.

## Source Rules

1. Write balanced S expressions such as `(node arg1 arg2)`.
2. Use bare symbols for identifiers and double quoted literals for strings.
3. Use `;` for a line comment. There is no block comment syntax.
4. Give each executable file one root form: `cli_app`, `http_server`, `web_app`, or `wasm_app`.
5. Put reusable declarations in a `module` root and import them with `(use "module.howl" as alias)`.
6. Prefer `use` for new modular code. `include` is a parser level splice retained by the current implementation, but the module design documents it as transitional.
7. Use only constructs with an implemented mapping for the intended target. The bytecode and direct execution paths deliberately cover bounded subsets.

Common forms include:

* Structure: `module`, `use`, `export`, `defun`, `lambda`, `struct`, `route`, `middleware`, and `test`.
* Flow: `let`, `try_let`, `set`, `if`, `match`, `for`, `while`, `do`, `call`, and `return`.
* Collections: `list`, `dict`, `append`, `map_set`, `map_delete`, `map_get`, and `list_get`.
* Strings and conversion: `str_split`, `str_join`, `regex_match`, `to_int`, `to_float`, `to_string`, and `bytes_to_string`.
* I/O and runtime: `read_file`, `write_file`, `mkdir`, `exec`, `sleep`, `print`, `cli_args`, `env`, `fetch`, and `spawn`.
* Adaptive operations: `llm_generate`, `fuzzy_cast`, `assert_semantic`, `semantic_match`, `neural_circuit`, `ephemeral_circuit`, `achieve`, `lazy_synthesize`, `optimize_block`, `optimize_signature`, `patch`, `with_context`, `spawn_agent`, and `task`.
* Native bytecode store: `store_open`, `store_put`, `store_get`, and `store_delete`.

Treat this list as syntax orientation, not a promise that every backend implements every form.

## Target Behavior

* The Go backend is the broadest target and emits `server.go` plus `server_test.go` when native tests are present.
* The JavaScript backend serves `web_app` programs and emits `app.js` plus `app.test.js` when tests are present.
* The legacy `wasm_app` backend emits `app.wat` for its bounded expression subset.
* `-compile-wasm` lowers a checked `cli_app` through typed SSA and CFG structures to WebAssembly Text. Unsupported layouts and operations return explicit backend errors.
* `-run` directly interprets a bounded `cli_app` subset without generating Go or JavaScript.
* `-compile-bc` passes through HFIR target verification, fails closed on unsupported constructs, and emits standalone bytecode for the HowlFrame VM.
* `-run-bc` enforces finite instruction limits and explicit capability grants. Do not weaken those controls to make a program run.

The `HFIR_TARGET_INFEASIBLE` diagnostic is part of the fail closed target contract. Preserve its code and source location behavior when changing target support.

## Build and Run Workflow

From the repository root:

```bash
go run howlframe.go examples/cli_hello.howl
go run server.go

go build -o howlframe howlframe.go
./howlframe -validate examples/cli_hello.howl
```

Direct execution:

```bash
go run howlframe.go -run examples/cli_hello.howl
```

Bytecode compilation and execution:

```bash
go run howlframe.go -compile-bc examples/cli_hello.howl -o /tmp/cli_hello.hfbc
go run howlframe.go -run-bc /tmp/cli_hello.hfbc
```

The default bytecode filename is `<input>.bc.bin`; use `.hfbc` when choosing an explicit HowlFrame branded artifact name.

Typed WebAssembly Text compilation:

```bash
go run howlframe.go -compile-wasm examples/native_math.howl -o /tmp/native_math.wat
```

Machine readable plans:

```bash
go run howlframe.go -mask-plan program.howl
go run howlframe.go -optimization-plan program.howl
```

Their emitted namespaces are `howlframe.mask_plan/v1` and `howlframe.optimization_plan/v1`.

`howlframe.go` is a normal Go source file with no exclusionary build tag. It participates in repository wide build, vet, and test commands. File explicit `go run howlframe.go ...` and `go build -o howlframe howlframe.go` remain the documented compiler invocations.

## Verification Workflow

After compiler, VM, HFIR, backend, module, or language changes, run:

```bash
gofmt -w .
go mod tidy
go test ./...
go vet ./...
go build ./...
```

Then exercise the affected execution paths directly. A representative set is:

```bash
go run howlframe.go -validate examples/cli_hello.howl
go run howlframe.go -run examples/cli_hello.howl
go run howlframe.go -compile-bc examples/cli_hello.howl -o /tmp/cli_hello.hfbc
go run howlframe.go -run-bc /tmp/cli_hello.hfbc
go run howlframe.go -compile-wasm examples/native_math.howl -o /tmp/native_math.wat
go test ./examples/repo_analyst -run TestRepoAnalystStandaloneBytecode
```

When changing module resolution, retain coverage for relative `.howl` imports, private symbols, missing imports, nested imports, circular imports, bytecode source independence, and HFIR provenance.

When changing generated output, inspect representative Go, JavaScript, WAT, bytecode, mask plan, and optimization plan artifacts. Successful source parsing alone does not prove that a generated artifact builds or executes.

Do not invoke paid external model calls solely to validate deterministic compiler changes.

## Optional Orchestrator

`tools/orchestrator/` is an optional local model experiment. Its current prompt and schema generate constrained JSON bytecode for execution by the HowlFrame VM. It is not required for ordinary `.howl` development. Test Python imports and schema loading without making paid model calls.

## Related Skills

Use the software development skill for general implementation quality, the test and verify skill for complete validation, automation for shell workflow changes, and commit and changelog for publication discipline.
