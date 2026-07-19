# Groom the Backlogs

Maintenance pass over `improvements.md`, `issues.md`, and `documentation/task_journals/`. Do not implement any backlog item during this pass.

**Subagents and delegation:** when re-verification fans out across many items or files, you may parallelize it with subagents or delegate it, subject to the delegation policy in `work_next_item.md`: read-only verification subagents (e.g. Claude Code's Explore agent) are allowed but bill the same plan as the session, so for limit-saving prefer headless Antigravity (`agy -p`) or local Ollama for self-contained verification briefs. All edits to the backlog documents, rankings, and journals stay in this session, and every claim a subagent or delegate reports must be spot-checked before it changes a row.

1. Re-evaluate every Pending row in both documents: is it still worth doing, and do its requirements still match the current code and environment? Update, merge, or close stale items with a dated note; keep table rows and detail sections in sync.
2. Re-rank where the ROI picture has changed, keeping each table's ranking rationale honest.
3. Promote durable knowledge from recent sessions and agent memories into the backlog documents or `documentation/` so it survives outside any one agent's memory.
4. Journals: delete any journal whose item is no longer outstanding, and consolidate any journal too large to skim, preserving its Next Step line.
5. Commit the grooming as `docs(backlog): <summary>` and push.
