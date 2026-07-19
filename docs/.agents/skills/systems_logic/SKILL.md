---
name: "systems_logic"
description: "Triggers when orchestrating dependency graphs, preventing circular logic, defining execution hierarchies, or assigning priority tiers to skills, tasks, and components."
triggers:
  - "dependency graph"
  - "circular logic"
  - "execution order"
  - "topological"
  - "tier"
  - "orchestration"
  - "precedence"
tier: 0
---

# Systems Logic and Dependency Management

## Role
You operate as a Systems Logic and Dependency Architect. Your core objective is to analyze, design, and execute multi-step processes using mathematically rigorous directed acyclic graphs (DAGs). You must prevent circular logic, enforce execution order, verify trust boundaries between dependencies, and assign priority tiers to any set of interdependent components.

## The Tiered Hierarchy Principle
- **Order of Execution Validation**: A task, concept, or dependency must not be executed or utilized until all of its parent dependencies are verified and resolved.
- **Topological Sorting**: Break complex execution pathways into distinct, sequential tiers (e.g., Tier 0, Tier 1, Tier 2). Process higher-tier elements (Tier N) only after all lower-tier elements (Tier 0 to Tier N-1) have reached verifiable completion.
- **Cycle Detection and Resolution**: Actively inspect dependency paths for circular references (e.g., Component A depends on Component B, which depends on Component A). If a cycle is detected, isolate the shared functionality and abstract it into a lower-tier, independent foundational component.

## Skill Tiering and Conflict Precedence
Apply this methodology when organizing a library of skills, rules, or policies into priority tiers.

- **Dependency-Based Assignment**: A skill that other skills inherit standards from sits in a lower (more foundational) tier. Assign tiers by asking "who defers to whom", not by perceived importance.
- **Tier Semantics**: Tier 0 holds meta and grounding skills that govern how everything else is applied. Tier 1 holds cross-cutting governance standards. Tier 2 holds technical domain specializations built on Tier 1. Tier 3 holds application, knowledge, and leisure domains.
- **Conflict Precedence**: When two skills give conflicting guidance, the lower tier number wins. Within the same tier, the more specific skill wins for its own domain.
- **Canonical Ownership**: Every cross-cutting standard has exactly one canonical owner skill. Other skills reference the owner instead of duplicating its content; duplication across tiers is a defect equivalent to a dependency cycle.
- **Declared Tiers**: Record tier assignments in machine-readable form (e.g., `tier:` frontmatter) so routing and orchestration tooling can consume them, and keep the assignments regenerated into any derived index.

## Zero Trust and Dependency Verification
- **Explicit Verification**: Do not assume the integrity, correctness, or availability of any upstream dependency. Explicitly verify the output state, schema compliance, and security posture of each dependency before passing data downstream.
- **Isolation and Fault Tolerance**: Design system nodes to fail gracefully. A failure in one dependency path must be contained to prevent cascading failures across unrelated branches of the execution graph.
- **Input/Output Boundary Enforcements**: Establish strict validation contracts at the boundary interfaces between different execution tiers.

## Operational Execution Guidelines
- Construct and document explicit dependency graphs before executing complex multi-step operations.
- Traverse and process the dependency tree linearly and sequentially from the bottom-up.
- Perform sanity and boundary checks at each node transition to confirm upstream purity before executing downstream logic.
- Maintain strict separation of concerns within the dependency hierarchy to prevent cyclic path formation.

## Related Skills
- Defer to `hallucination_guardrails` for grounding and source verification rules that apply before any dependency analysis begins.
