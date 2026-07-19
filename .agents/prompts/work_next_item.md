# Work the Next Backlog Item

Work exactly one item end to end, leaving the repository in a state where this chat can be cleared and the next session starts with zero context.

## 1. Select

- Check `documentation/task_journals/` first (ignore `TEMPLATE.md`). If a journal for an in-flight item exists, resume that item instead of starting a new one.
- Run `git worktree list` and look for local or remote unmerged branches whose names suggest agent worktrees (e.g. `worktree-*` branches, or anything under `.claude/worktrees/`). If a worktree or unmerged worktree branch exists, inspect it before selecting: an uncommitted task journal inside a worktree counts as a resume point exactly as if it were in `documentation/task_journals/`, and unmerged commits on a worktree branch may mean a whole item is already done and just needs merging and closing out rather than redoing.
- Otherwise read the ranked tables in `issues.md` and `improvements.md` and pick the single highest-priority open item across both. Bugs outrank improvement work of similar score, per the rule in `issues.md`.
- **Below-floor gate:** never silently pick an item flagged `⚠️ below floor` (score under the 0.5 ROI floor defined in `improvements.md`). Skip past it to the highest-scoring above-floor item, and tell the user which flagged items were skipped so they can confirm one (work it anyway), re-scope it until it clears the floor, or close it. Work a below-floor item only on the user's explicit confirmation in the current session.

## 2. Re-evaluate before implementing

- Confirm the item is still worth doing and that its stated requirements still match the current code and environment; both may have changed since the item was filed.
- If it is stale, update the row and detail section, merge it into another item, or close it with a dated note explaining why. A well-documented closure counts as completing this run.

## 3. Execute, delegating the heavy work to non-Claude models

This session is the orchestrator, not the implementer. To preserve Claude session limits, keep only selection, re-evaluation, backlog and journal edits, verification, and the commit in this session; delegate the implementation itself to a non-Claude model.

- Follow the Working Protocol in `improvements.md`: open a task journal from `documentation/task_journals/TEMPLATE.md`, route the matching skills, scan for free tools, and read the item's detail section before writing the delegation brief.
- Write a self-contained brief for the delegate: the item's detail section, the specific files involved, the tests to add or update, and the relevant protocol constraints (test commands, commit conventions do not apply to the delegate; it edits only). The delegate starts with zero repository context, so the brief must stand alone.
- Pick the delegate from what is live right now, starting from the item's Gemini model column:
  - **Antigravity CLI (headless):** `agy -p "<brief>" --model "<model>" --mode accept-edits --print-timeout 30m`. Headless agy does not treat the invocation directory as its workspace — on 2026-07-19 a delegate could not find repo-relative paths at all — so always give absolute file paths in the brief. **Always verify the claimed diff before trusting it:** on 2026-07-19 GPT-OSS 120B via agy returned a detailed, plausible "Changed files" table describing exactly the right edits after running for several minutes, but made zero real changes anywhere on disk (`git status` was clean, `grep` for the new symbols found nothing, and a filesystem-wide mtime search including agy's own cache dirs found no trace). Unlike a quota error, this failure is silent and self-reports success. Run `git status`/`git diff` after every delegation, before reading its summary as fact. If the brief contains backticks (e.g. quoting Go/Python identifiers), write it to a file and pass it as `agy -p "$(cat brief.txt)"` rather than inline in a double-quoted string — bash treats backticks as command substitution even inside double quotes, so an inline brief with backticks silently corrupts or errors (hit live on 2026-07-19); `$(cat ...)`'s output is inserted as literal text and is not re-parsed for nested substitution. Also run the `agy -p` command with a Bash timeout well above the tool's 2-minute default (or `run_in_background: true`) — `--print-timeout` only bounds agy's own internal wait, not the calling shell's timeout, and a real edit can take several minutes (hit live on 2026-07-19: cut off at the tool's default before completing). List live model names with `agy models`; on a quota error try another tier before giving up, but expect the Gemini tiers (Flash and Pro) to share one account-wide quota — on 2026-07-19 all three failed together with an identical reset time — while GPT-OSS 120B errors independently. When Antigravity is fully unavailable, fall back to local Ollama for drafting and apply trivial fully-specified edits directly. Antigravity's Claude Sonnet and Opus models bill the Google subscription, not Claude Code limits, and are a valid escalation for hard items.
  - **Local Ollama:** for small, well-bounded subtasks (draft a function, review a diff, write a doc section) where a local model suffices. Check live tags with `curl localhost:11434/api/tags`.
  - Never delegate to Claude Code subagents (the Agent tool) for limit-saving; they bill the same Claude plan as this session.
- Require a clean `git status` before launching a delegate so its diff is exactly attributable. Afterward, review the full `git diff` yourself, run the tests yourself (`make test-changed`, then `make test`), and either fix small gaps directly or re-delegate with concrete feedback. Never commit a delegate's work unreviewed.
- Update the journal and commit it at every milestone, recording each delegation (model, brief summary, outcome) and keeping its Next Step line current so a fresh session can resume from the journal alone after a session limit or power outage.

## 4. Close the loop

- Verify the change end to end, run the full `make test`, commit as `<type>(<scope>): <description>`, set the item's Status to `Done (YYYY-MM-DD)` with a Done note, delete this task's journal in the final commit, and push.
- Record findings discovered during the work as new rows plus detail sections in `improvements.md` or `issues.md`, following each document's structure and ranking rationale.
- Promote anything durable learned this session (constraints, decisions, environment facts) into the backlog documents or `documentation/`, not only into agent memory.
- Housekeeping: delete any journals whose items are no longer outstanding, and consolidate any journal that has grown too large to skim. Also, any worktree branch whose work is finished must be merged and its worktree removed (`git worktree remove`, delete the branch) before the session ends, so no stranded worktrees survive the session.

Done means: clean `git status`, work pushed, no journal left for the finished item, and new findings filed where the next session will see them.
