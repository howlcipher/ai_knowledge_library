# Prompt Library

Reusable task prompts for any agent working in this repository. Each `.md` file here is the canonical prompt; per-agent wrappers only point at it, mirroring the `AGENTS.md` entry-point pattern. Edit the canonical file only, never the wrappers.

## Prompts

| Prompt | Purpose |
| --- | --- |
| `work_next_item.md` | Work the single highest-priority open item across `issues.md` and `improvements.md`, end to end, per the Working Protocol |
| `resume_task.md` | Resume an interrupted task from its journal in `documentation/task_journals/` |
| `groom_backlogs.md` | Re-evaluate, re-rank, and clean up both backlogs and stale journals without implementing anything |

## Invocation

- **Claude Code:** slash commands from `.claude/commands/`, e.g. `/work_next_item`. Each wrapper inlines the canonical prompt with an `@` file reference.
- **Gemini CLI:** custom commands from `.gemini/commands/`, e.g. `/work_next_item`. Each wrapper instructs the model to read and follow the canonical file.
- **Any other agent:** paste "Read `.agents/prompts/<name>.md` and follow it exactly."

## Adding a prompt

1. Create `.agents/prompts/<snake_case_name>.md` with the full instructions. Reference existing protocols (for example the Working Protocol in `improvements.md`) instead of duplicating them, so the prompt cannot drift from the source of truth.
2. Add a matching wrapper in `.claude/commands/<name>.md` and `.gemini/commands/<name>.toml`, copying an existing wrapper's shape.
3. Add a row to the table above.
