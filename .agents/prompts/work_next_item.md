# Work the Next Backlog Item

Work exactly one item end to end, leaving the repository in a state where this chat can be cleared and the next session starts with zero context.

## 1. Select

- Check `documentation/task_journals/` first (ignore `TEMPLATE.md`). If a journal for an in-flight item exists, resume that item instead of starting a new one.
- Otherwise read the ranked tables in `issues.md` and `improvements.md` and pick the single highest-priority open item across both. Bugs outrank improvement work of similar effort, per the rule in `issues.md`.

## 2. Re-evaluate before implementing

- Confirm the item is still worth doing and that its stated requirements still match the current code and environment; both may have changed since the item was filed.
- If it is stale, update the row and detail section, merge it into another item, or close it with a dated note explaining why. A well-documented closure counts as completing this run.

## 3. Execute

- Follow the Working Protocol in `improvements.md` exactly: open a task journal from `documentation/task_journals/TEMPLATE.md`, re-evaluate the model against what is currently available, route the matching skills, scan for free tools, read the item's detail section, then implement with tests.
- Update the journal and commit it at every milestone, keeping its Next Step line current so a fresh session can resume from the journal alone after a session limit or power outage.

## 4. Close the loop

- Verify the change end to end, run the full `make test`, commit as `<type>(<scope>): <description>`, set the item's Status to `Done (YYYY-MM-DD)` with a Done note, delete this task's journal in the final commit, and push.
- Record findings discovered during the work as new rows plus detail sections in `improvements.md` or `issues.md`, following each document's structure and ranking rationale.
- Promote anything durable learned this session (constraints, decisions, environment facts) into the backlog documents or `documentation/`, not only into agent memory.
- Housekeeping: delete any journals whose items are no longer outstanding, and consolidate any journal that has grown too large to skim.

Done means: clean `git status`, work pushed, no journal left for the finished item, and new findings filed where the next session will see them.
