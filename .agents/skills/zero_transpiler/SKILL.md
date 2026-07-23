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

## AST Node Reference

### Roots & Structure
- `(http_server port blocks...)`, `(cli_app blocks...)`
- `(route "path" (lambda (req) body))`
- `(defun name (args...) body)` — args accept `(type_hint var "Type")`
- `(struct Name (field Type)...)`
- `(import "package")`
- `(include "file.zero")` — resolves relative to the including file's own directory (bug #6, fixed); does not follow renamed/moved targets (see bug #15 below).

### Control Flow & Variables
- `(let (var val) body)` — chain by nesting another `let` inside `body`.
- `(try_let (var val) (catch err catchBody) successBody)` — generalized to any function returning `(value, error)` (bug #8, fixed).
- `(set var val)`
- `(if (op a b) then [else])` — ops: `=`, `!=`, `<`, `>`, `<=`, `>=`; else branch is optional (bug #16, fixed) — `(if cond then)` omits the Go `else` clause entirely. **Condition must be a flat `(op a b)` — `and`/`or` and compound operands (`(> (+ 2 3) 4)`) are not supported yet** (see Known Bugs, bug #18).
- `(match var (val body)... (default body))`
- `(for item list body)`, `(while (op a b) body)`
- `(do stmts...)`
- `(call func args...)`
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
- `(read_file "path")` → `([]byte, error)` — **not** a string; see Known Bugs for the coercion gap.
- `(write_file "path" data)`, `(mkdir "path")`, `(exec "cmd" args...)` → `([]byte, error)`
- `(sleep ms)`, `(print args...)`, `(cli_args)` / `(cli_args index)`

### Data Structures & Strings
- `(list items...)`, `(dict ("k" "v")...)`
- `(append list item)`, `(map_set dict key val)`, `(map_delete dict key)`
- `(str_split s sep)`, `(str_join list sep)`, `(regex_match pattern s)`

### Math & Logic
- `+ - * /`, `and`, `or` — e.g. `(+ 1 2)`.

### Native Tests
- `(test "description" body)` inside `cli_app`/`http_server` — extracted into `server_test.go` (`_test.go` Go tests).

### Advanced (use sparingly, verify against `zero.go` first — newer/less battle-tested)
- `(patch funcName newBody)` — AST-level surgical patch of an existing `defun` without rewriting the file.
- `(with_context (vars...) body)` — implicit context threading; auto-injects listed vars into `call` sites inside the block.

## Known Bugs — must-follow workarounds

Check `bugs.md` in the zero repo for current status before relying on any of these; do not assume a bug is fixed just because it's listed here as "Pending" at some point in the past — re-grep `bugs.md` if the fix date matters.

- **`if` else branch is optional (bug #16, fixed 2026-07-23)**: `(if cond then)` now parses and omits the Go `else` clause entirely; both 3-child and 4-child forms work.
- **`if` condition rejects `and`/`or` and silently mis-compiles compound operands (bug #18, pending)**: the condition parser only accepts a flat `(op literal literal)` — `(if (and (> a 1) (< a 10)) ...)` errors with `unsupported operator in if cond: and`, and a compound operand like `(if (> (+ 2 3) 4) ...)` produces **no error at all** but emits corrupted Go (`if  > 4 {`, empty operand). Don't nest arithmetic or `and`/`or` directly inside an `if` condition — bind to a `let` variable first and compare the variable.
- **`return` now handles compound expressions (bug #13, fixed 2026-07-23)**: `(return (+ a b))` and `(return (call f x))` both work correctly (recurses via `generateStatementRaw`). No more need to bind to a `let` variable first purely to work around this.
- **`//line` directive can corrupt a compound expression nested inside another compound expression (bug #19, pending)**: several codegen paths (binary operators `+ - * / < > and or ==`, `assert_semantic`, `cli_args` index) embed a recursive `generateStatement` result *inside* a larger expression string; if the nested node's head is one of the heads that get a `//line` prefix (notably `call`), that comment splices mid-expression and corrupts the output — e.g. `(+ (call f) 1)` transpiles with no error but fails `go build`. Symptom: transpile succeeds, `go build` fails with a garbled statement near a `//line` comment. Workaround: bind any `call` (or other wrapped-head expression) used as an operand to a `let` variable first, then reference the variable.
- **No string→number primitive (bug #17, pending)**: there is no `to_int`/`to_float`/`parse_number` node. The only coercion path is `fuzzy_cast`, which round-trips through an LLM (needs Ollama) — wildly disproportionate for turning `"42"` into `42`. Don't reach for arithmetic on data read from `read_file`/`cli_args`/`str_split` without flagging this gap to the user.
- **`read_file` returns `[]byte`, not `string`** (related finding under bug #17): passing it straight to `str_split`/string ops fails to compile. The only known working escape hatch is `(call string content)` — `call`'s codegen emits `funcName(args)` for any symbol, including Go builtins, so this is an undocumented accident, not a supported feature. Prefer flagging the gap over relying on it.
- **`(import "pkg")` can duplicate/go unused (bug #14, pending)**: combining a custom `import` that collides with the transpiler's default import list, or combining `import` with `test` blocks that don't reference it inside the test body, can produce a Go compile error in `server.go`/`server_test.go`. Keep custom imports minimal and referenced from both normal code and any `test` blocks in the same file.
- **`include` path targets can go stale (bug #15, pending)**: relative-to-including-file resolution (bug #6) doesn't help if the *target* file was moved; the include path itself must be updated by hand.

## Build & Run Workflow

The transpiler always writes output to `server.go` (and `server_test.go` if the file has `test` blocks) in the current directory, regardless of `cli_app` vs `http_server` root — always `cd` into the zero repo (or wherever `zero.go` lives) before invoking it.

```bash
# Transpile + run in one step
go run zero.go yourfile.zero && go run server.go

# Or build a standalone binary
go run zero.go yourfile.zero
go build -o app server.go
./app
```

On a semantic error, the transpiler prints a single JSON line to stdout and exits 1:
```json
{"reason": "...", "line": N, "column": N}
```
Feed this back verbatim into the next generation attempt for self-correction — don't paraphrase the reason string.

`orchestrator.py` in the zero repo automates this generate → transpile → feedback → retry loop using `outlines` for grammar-constrained generation against a local Ollama model; its EBNF grammar must be updated (improvement #3) whenever a new AST node is added to `zero.go`, or the orchestrator won't be able to emit it.

## Testing

- Prefer native `(test "..." body)` blocks over external Go test scaffolding — they compile straight into `_test.go` via the transpiler.
- After any change to `zero.go` itself, run the full fixture suite: `for f in tests/*.zero; do go run zero.go "$f"; done`, then `go build server.go` to confirm generated code actually compiles (transpile success does not guarantee `go build` success — see bugs #18 and #19, both silent-corruption cases).
- `tests/test_include.zero` is currently a known-broken fixture (bug #15) — don't treat its failure as a new regression.

## Related Skills
- Defer to [[software_development]] for general clean-code and modularity standards that apply to any `defun` body or project layout decisions outside the language's own grammar.
- Defer to [[automation]] for shell scripting around the transpile/build/run loop itself.
- Defer to [[commit_and_changelog]] and the zero repo's own `improvements.md`/`bugs.md` Working Protocol when landing changes to `zero.go`.
