# Resume an In-Flight Task

A previous session was interrupted (session limit, power outage, cleared chat). Continue its work from the journal alone.

1. List `documentation/task_journals/` (ignore `TEMPLATE.md`), and also run `git worktree list` and check for local or remote unmerged worktree branches (e.g. `worktree-*`, or anything under `.claude/worktrees/`). A journal committed only inside a worktree, or unmerged commits on a worktree branch, count as in-flight work to resume. Only when neither a journal nor stranded worktree work exists, say nothing is in flight and suggest `work_next_item` instead.
2. If several journals exist, resume the one named in the invocation arguments; with no argument, resume the most recently modified.
3. Read the journal's Summary, Pre-Flight Re-Evaluation, Progress Log, and Next Step. Verify its claims against the working tree, `git status`, and `git log` before acting; the interruption may have lost or half-applied work.
4. Continue from the Next Step line, following the Working Protocol in `improvements.md`, and close the item per that protocol: tests, end to end verification, commit, mark Done, delete the journal in the final commit, push.
