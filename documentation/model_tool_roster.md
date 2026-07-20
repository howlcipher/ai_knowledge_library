# Model and Tool Roster

## Models

1. **Claude Pro subscription (Claude Code).** The orchestrating session itself. Claude Code subagents (the Agent tool) bill the same Claude plan and do NOT save session limits — never delegate to them for limit-saving purposes.
2. **Google subscription via Antigravity CLI (`agy`).** List live model names with `agy models` before picking one — do not assume a fixed list. As of the last check (2026-07-19) the available names included: Gemini 3.5 Flash (Medium/High/Low), Gemini 3.1 Pro (Low/High), Claude Sonnet 4.6 (Thinking), Claude Opus 4.6 (Thinking), and GPT-OSS 120B (Medium) — but state explicitly in the doc that this exact list will drift and `agy models` is the source of truth, not this snapshot.
   - Invocation pattern: `agy -p "<brief>" --model "<model>" --mode accept-edits --print-timeout 30m`.
   - Antigravity's Claude Sonnet/Opus models bill the Google subscription, not Claude Code limits — a valid escalation path for hard items without spending Claude session budget.
3. **Local Ollama.** Check live tags with `curl localhost:11434/api/tags` before assuming a model is pulled — do not hardcode tag names, they change. Good for small, well-bounded subtasks (drafting a function, reviewing a diff, writing a doc section) where a local model suffices.

## Delegation lessons (Antigravity / agy)

- Headless `agy` does NOT treat the invocation directory as its workspace — a delegate could not find repo-relative paths at all. Always give absolute file paths in the brief.
- **Always verify the claimed diff before trusting it.** GPT-OSS 120B via agy once returned a detailed, plausible "Changed files" table describing exactly the right edits after running for several minutes, but made zero real changes anywhere on disk (`git status` was clean, `grep` for the new symbols found nothing, and a filesystem-wide mtime search including agy's own cache dirs found no trace). Unlike a quota error, this failure is silent and self-reports success. Run `git status`/`git diff` after every delegation, before reading its summary as fact.
- If the brief contains backticks (e.g. quoting Go/Python identifiers), write it to a file and pass it as `agy -p "$(cat brief.txt)"` rather than inline in a double-quoted string — bash treats backticks as command substitution even inside double quotes, so an inline brief with backticks silently corrupts or errors. `$(cat ...)`'s output is inserted as literal text and is not re-parsed for nested substitution.
- Run the `agy -p` command with a Bash timeout well above the tool's 2-minute default (or run it in the background) — `--print-timeout` only bounds agy's own internal wait, not the calling shell's timeout, and a real edit can take several minutes.
- List live model names with `agy models`; on a quota error try another tier before giving up, but expect the Gemini tiers (Flash and Pro) to share one account-wide quota — all three once failed together with an identical reset time — while GPT-OSS 120B errors independently.
- When Antigravity is fully unavailable, fall back to local Ollama for drafting, and apply trivial fully-specified edits directly.
- GPT-OSS 120B via agy has twice (item 34, and again while writing this very doc for item 18) rendered plain compound-word hyphens as the Unicode non-breaking hyphen (U+2011) instead of ASCII `-` in generated prose. Check delegated markdown/prose for this with `grep -n $'\xe2\x80\x91' <file>` before committing, and fix with a plain string substitution back to `-`.

## Discovery sources (when the roster has no fit)

- **There's An AI For That** (theresanaiforthat.com) — directory of AI tools/models by task category.
- **MCP server registry** — for finding free Model Context Protocol servers that extend agent capability (e.g. web search, file systems, specialized APIs).
- **Package indexes** (PyPI, npm, Go module proxy, etc.) — for free open-source libraries/CLIs that solve a subtask without needing a new paid service.

## Hard rule

> Anything free and already available may be used autonomously. Anything paid, requiring signup, requiring a new API key, or needing a new install must be discussed with the user first.
