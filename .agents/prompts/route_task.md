# Route Engineering Task

Analyze a task's objective, requirements, and constraints, and deterministically assign it to an appropriate agent type and independent reviewers using the control plane router.

## 1. Inputs

- **Task specification:** `TaskSpec` file or natural language task description.
- **Repository context:** Read project rules in `AGENTS.md` and local stack markers.

## 2. Procedure

1. Extract task characteristics:
   - Risk level: `low`, `medium`, `high`, `critical`.
   - Required skills from `.agents/skills/`.
   - Reasoning tier: `tier_1` (architecture/high-risk/security), `tier_2` (standard feature/bugfix), `tier_3` (mechanical/local drafting).
   - Tool requirements and constraints.
2. Execute the deterministic router:
   ```bash
   python -m src.control_plane route-task --task-file <task_spec.yaml>
   ```
   Or evaluate the declarative agent capability registry in `src/control_plane/agent_registry.py`.
3. Check for user overrides. If the user explicitly requested a specific agent, honor it and record it as an override.
4. Record the routing decision, assigned agent type, reasoning tier, and recommended independent reviewer roles in the task journal.
