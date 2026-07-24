---
name: "zero_transpiler"
description: "Syntax rules, AST node reference, known transpiler bugs, and build workflow for Zero, the Lisp-like AI-first language that transpiles to Go."
triggers:
  - "zero"
  - ".zero"
  - "zero.go"
  - "zero language"
  - "zero transpiler"
  - "s-expression"
  - "lisp-like"
tier: 3
---

# Zero Transpiler

Zero is a Lisp-like, AI-first language that transpiles to Go, developed locally at `/run/media/system/tallgeese/dev/zero/` and published at https://github.com/howlcipher/zero. It exists so LLMs can emit simple, structurally-guaranteed S-expressions instead of hallucinating Go syntax directly; the transpiler (`zero.go`) catches semantic errors and returns a localized JSON error for self-correction loops.

This skill is the canonical Zero language reference for any agent writing `.zero` code or working on the transpiler itself. Prefer this file over recalling the grammar from memory — the language is small and versioned, and bugs.md/improvements.md in the zero repo are the live source of truth for what currently works.

## Core Syntax Rules

1. **S-expressions only**: `(node arg1 arg2)`, always balanced parentheses.
2. **No raw Go**: only emit primitives with an explicit AST mapping in `zero.go`.
3. **Symbols vs strings**: bare identifiers (`req`, `my_var`) are symbols; string literals need double quotes (`"Hello"`).
4. **Exactly one root node per file**: `(http_server port routes...)` for web apps, or `(cli_app statements...)` for CLI scripts.
5. **Comments**: `;` starts a line comment, consumed to end-of-line (bug #23, fixed 2026-07-23) — e.g. `;; explains the next form`. No block-comment syntax exists.

## AST Node Reference

### Roots & Structure
- `(http_server port blocks...)`, `(cli_app blocks...)`
- `(route "path" (lambda (req) body))`
- `(defun name (args...) body)` — args accept `(type_hint var "Type")`, or the terser combined `(type_hints (a int) (b int) (return int))` form. `(type_hint return "void")` now works (bug #24, fixed 2026-07-23) for a pure side-effect function with no `return`.
- `(struct Name (field Type)...)`
- `(import "package")`
- `(include "file.zero")` — resolves relative to the including file's own directory (bug #6, fixed).

### Control Flow & Variables
- `(let (var val) body)` — chain by nesting another `let` inside `body`.
- `(try_let (var val) (catch err catchBody) successBody)` — generalized to any function returning `(value, error)` (bug #8, fixed).
- `(set var val)`
- `(if cond then [else])` — else branch is optional (bug #16, fixed) — `(if cond then)` omits the Go `else` clause entirely. `cond` can be a compound/logical expression (`and`/`or`, nested arithmetic on either side) as of bug #18 (fixed 2026-07-24) — `(if (and (> a 1) (< a 10)) ...)` and `(if (> (+ 2 3) 4) ...)` both work correctly now.
- `(match var (val body)... (default body))`
- `(for item list body)`, `(while cond body)` — `while`'s condition supports the same compound/`and`/`or` forms as `if` (same bug #18 fix).
- `(do stmts...)`
- `(call func args...)` — compound-expression arguments (nested `call`, arithmetic) now pass through correctly (bug #20, fixed).
- `(spawn (lambda () body))` — goroutine.

### Web & HTTP
- `(res status "content-type" body)`, `(res_json status data)`
- `(parse_json Type body)`
- `(fetch url method)` → `([]byte, error)`

### AI Primitives
- `(llm_generate "prompt" ["model"])` → `(string, error)`
- `(fuzzy_cast Type var ["model"])` → `(Type, error)` — coerces messy text to a struct via an LLM round-trip.
- `(assert_semantic var "condition")` → bool, qualitative/natural-language constraint check.

### Automation & I/O
- `(read_file "path")` → `([]byte, error)` — use `(to_string b)`/`(bytes_to_string b)` (bug #17, fixed) to convert to a real Go string rather than the undocumented `(call string b)` escape hatch.
- `(write_file "path" data)`, `(mkdir "path")`, `(exec "cmd" args...)` → `([]byte, error)`
- `(sleep ms)`, `(print args...)`, `(cli_args)` / `(cli_args index)`
- `(to_int s)`, `(to_float s)` (bug #17, fixed) — deterministic string→number, no LLM round-trip needed; only reach for `fuzzy_cast` for genuinely messy/unstructured input.

### Data Structures & Strings
- `(list items...)`, `(dict ("k" "v")...)` — work in any expression position now (a `return` value, a `print`/`call` argument, nested inside another `list`/`dict`, not just a `let` binding's direct value; bug #26, fixed 2026-07-24). Compound-expression **elements/values** (e.g. `(list (call one) "b")`, `(dict ("k" (call one)))`) construct correctly in the Go backend too (bug #27, fixed 2026-07-24). One gap remains: a `dict` **key** that is itself a compound expression (e.g. `(dict ((call k) "v"))`) still silently drops to empty, producing invalid Go (`map[string]string{: "v"}`) — bug #28, open, below the ROI floor. Stick to literal string/symbol keys until #28 ships.
- `(append list item)`, `(map_set dict key val)`, `(map_delete dict key)`, `(map_get dict key)`, `(list_get list idx)` (improvement #60, fixed 2026-07-24) — `map_get` returns `""` on a missing key (Go zero-value semantics); `list_get` is bounds-checked and returns `""` on an out-of-range index rather than panicking, mirroring `cli_args`' existing safer convention.
- `(str_split s sep)`, `(str_join list sep)`, `(regex_match pattern s)`

### Math & Logic
- `+ - * /`, `and`, `or` — e.g. `(+ 1 2)`.

### Native Tests
- `(test "description" body)` inside `cli_app`/`http_server` — extracted into `server_test.go` (`_test.go` Go tests).

### Advanced (use sparingly, verify against `zero.go` first — newer/less battle-tested)
- `(patch funcName newBody)` — AST-level surgical patch of an existing `defun` without rewriting the file.
- `(with_context (vars...) body)` — implicit context threading; auto-injects listed vars into `call` sites inside the block.

## Known Bugs — must-follow workarounds

As of 2026-07-24 (a later pass, after bugs #27 and #28), `bugs.md` has one open bug: #28, `dict` literal keys silently dropping compound expressions to empty (see the Data Structures section above) — filed below the ROI floor, so it's open but not scheduled. Every other bug is Done. Check `bugs.md` in the zero repo for current status before relying on this statement in a future session; do not assume it still holds without re-checking, since new bugs get filed as they're found. Notable fixes worth knowing about (all confirmed fixed, not just table-status "Done" — several had stale detail-section notes contradicting their own table status until the 2026-07-24 groom pass corrected them):

- **`list`/`dict` literals work in any expression position (bug #26, fixed 2026-07-24)**: no longer restricted to a `let` binding's direct value — a `return` value, `print`/`call` argument, or nesting inside another `list`/`dict` all work now.
- **Go backend's `list`/`dict` elements/values handle compound expressions (bug #27, fixed 2026-07-24)**: `(list (call one) "b")` and `(dict ("k" (call one)))` no longer silently drop the compound element/value to an empty string. Dict *keys* still have this gap — see bug #28 above.
- **`if`/`while` conditions support `and`/`or` and compound operands (bug #18, fixed 2026-07-24)**: `(if (and (> a 1) (< a 10)) ...)` and `(if (> (+ 2 3) 4) ...)` both work correctly, for both `if` and `while`. Landed as a side effect of improvement #53's IR refactor.
- **`return`/`call` handle compound expressions correctly (bugs #13, #19, #20, all fixed)**: `(return (+ a b))`, `(return (call f x))`, and `(call f (call g 1))`-style nested arguments all work — no more need to bind to a `let` variable first purely to work around silent drops or `//line`-corrupted output.
- **String↔number/bytes conversion primitives exist (bug #17, fixed)**: `(to_int s)`, `(to_float s)`, `(to_string b)`, `(bytes_to_string b)` — deterministic, no LLM round-trip needed. Only reach for `fuzzy_cast` for genuinely messy/unstructured input.
- **Void `defun` supported (bug #24, fixed)**: `(type_hint return "void")` works for pure side-effect functions.
- **`(import "pkg")` duplication/unused fixed (bug #14)**: custom imports colliding with the default import list are deduped, and `server_test.go` only includes imports actually referenced inside `test` bodies.
- **`if` else branch is optional (bug #16, fixed)**: `(if cond then)` omits the Go `else` clause entirely; both 3-child and 4-child forms work.
- **Collections support random-access reads (improvement #60, fixed 2026-07-24)**: `(map_get dict key)` and `(list_get list idx)` read a value back out by key/index — no more whole-collection-printing-only workaround. `map_get` returns `""` on a missing key; `list_get` is bounds-checked and returns `""` out of range rather than panicking.

**Known, non-bug environment gotcha:** `tests/test_schema.zero` uses `github.com/mattn/go-sqlite3`, correctly declared in `go.mod` — but `go.sum` is deliberately `.gitignore`d, so a fresh clone needs a local `go mod tidy` (confirmed working with network access) before that fixture's generated code will `go build`. Not a transpiler defect.

## Build & Run Workflow

The transpiler always writes output to `server.go` (and `server_test.go` if the file has `test` blocks) in the current directory, regardless of `cli_app` vs `http_server` root — always `cd` into the zero repo (or wherever `zero.go` lives) before invoking it.

```bash
# Transpile + run in one step
go run zero.go yourfile.zero && go run server.go

# Or build a standalone binary
go run zero.go yourfile.zero
go build -o app server.go
./app

# Or interpret a cli_app script directly (improvement #49 Phase 1, added 2026-07-24):
# no server.go ever written, no go build/go run invoked. Only a bounded subset
# of the language is covered (control flow, functions, math/string/collection
# ops) — see docs/direct_execution_design.md in the zero repo for exact
# coverage; http_server/web_app roots and try_let-dependent primitives
# (read_file, db_connect, etc.) aren't supported under -run yet.
go run zero.go -run yourfile.zero
```

On a semantic error, the transpiler prints a single JSON line to stdout and exits 1:
```json
{"reason": "...", "line": N, "column": N}
```
Feed this back verbatim into the next generation attempt for self-correction — don't paraphrase the reason string.

`orchestrator.py` in the zero repo automates this generate → transpile → feedback → retry loop using `outlines` for grammar-constrained generation against a local Ollama model; its EBNF grammar must be updated (improvement #3) whenever a new AST node is added to `zero.go`, or the orchestrator won't be able to emit it.

**Implementation note:** `zero.go` carries `//go:build ignore` specifically so `go build .`/`go vet ./...`/`go test ./...` in the repo root (used to verify *generated* `server.go` output) don't try to compile the transpiler's own source alongside it. This means `go run zero.go yourfile.zero` — naming the file explicitly — is the only supported invocation; a second `.go` file for transpiler-internal code would need to be named explicitly on every invocation too (a breaking change discovered and reverted while building the Phase 1 interpreter above, which is why it lives inside `zero.go` itself rather than a separate file).

## Testing

- Prefer native `(test "..." body)` blocks over external Go test scaffolding — they compile straight into `_test.go` via the transpiler.
- After any change to `zero.go` itself, run the full fixture suite: `for f in tests/*.zero; do ./zero "$f"; go build -o /tmp/servercheck . ; rm -f server.go server_test.go; done` (never bare `go build .` in the repo root — see Build & Run Workflow) to confirm generated code actually compiles (transpile success does not guarantee `go build` success).
- `tests/routes.zero` is an `include`-only module fragment, not a standalone root — its own transpile failure as a root file is expected, not a regression.

## Related Skills
- Defer to [[software_development]] for general clean-code and modularity standards that apply to any `defun` body or project layout decisions outside the language's own grammar.
- Defer to [[automation]] for shell scripting around the transpile/build/run loop itself.
- Defer to [[commit_and_changelog]] and the zero repo's own `improvements.md`/`bugs.md` Working Protocol when landing changes to `zero.go`.
