# Prompt Library

Reusable task prompts for any agent working in this repository. Each `.md` file here is the canonical prompt; per-agent wrappers only point at it, mirroring the `AGENTS.md` entry-point pattern. Edit the canonical file only, never the wrappers.

## Prompts

| Prompt | Purpose |
| --- | --- |
| `work_next_item.md` | Work the single highest-priority open item across `issues.md` and `improvements.md`, end to end, per the Working Protocol, delegating implementation to non-Claude models to preserve Claude session limits |
| `resume_task.md` | Resume an interrupted task from its journal in `documentation/task_journals/` |
| `groom_backlogs.md` | Re-evaluate, re-rank, and clean up both backlogs and stale journals without implementing anything |
| `route_task.md` | Deterministically classify and route a task specification to an agent and reviewers |
| `review_change.md` | Conduct specialized independent reviews to falsify correctness and uncover defects |
| `reconcile_reviews.md` | Reconcile findings across multiple reviewers without silent dismissal of defects |
| `verify_change.md` | Execute deterministic verification suites and capture verifiable evidence |
| `ship_check.md` | Verify evidence and evaluate human authority boundaries before completion |

## Invocation

- **Claude Code:** command skills from `.agents/skill_commands/<name>/SKILL.md`, e.g. `/work_next_item`. Each wrapper inlines the canonical prompt with an `@` file reference. These are symlinked into `.claude/skills/` (project scope, auto-rebuilt by `scripts/generate_skills_manifest.py`) and, on any machine that has run `scripts/install_global.sh`/`.ps1`, into `~/.claude/skills/` too (global scope, works from any directory).
- **Codex:** skills from `.agents/skill_commands/<name>/SKILL.md`, e.g. `$work_next_item`. Codex discovers them in the repository and the global installer links them into `~/.agents/skills/` for use from any directory. Each wrapper resolves its canonical prompt relative to its own `SKILL.md`.
- **Gemini CLI:** custom commands from `.gemini/commands/`, e.g. `/work_next_item`. Each wrapper instructs the model to read and follow the canonical file.
- **Devin CLI:** skills from `.devin/skills/<name>/SKILL.md`, e.g. `/work_next_item`. Each wrapper instructs the model to read and follow the canonical file.
- **Any other agent:** paste "Read `.agents/prompts/<name>.md` and follow it exactly."

## Adding a prompt

1. Create `.agents/prompts/<snake_case_name>.md` with the full instructions. Reference existing protocols (for example the Working Protocol in `improvements.md`) instead of duplicating them, so the prompt cannot drift from the source of truth.
2. Add matching wrappers at `.agents/skill_commands/<name>/SKILL.md` (Claude/Codex), `.gemini/commands/<name>.toml` (Gemini CLI), and `.devin/skills/<name>/SKILL.md` (Devin CLI). Do not hand edit `.claude/skills/` — rerun `python scripts/generate_skills_manifest.py` (or just commit; the pre-commit hook does it automatically) to symlink the new command skill in.
3. Add a row to the table above.
