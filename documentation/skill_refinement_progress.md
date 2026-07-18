# Skill Refinement Progress Tracker

Working checklist for the skill library refinement improvement. This document is the single source of truth for resuming the effort if a session ends mid-flight: read the phase status, find the first unchecked row, and continue. Update the status tables and commit at every phase boundary and batch boundary.

## Objective

Refine all `.agents/skills/*/SKILL.md` files against a shared rubric, organize them into priority tiers using the `systems_logic` methodology, deduplicate overlapping content across skill clusters, and finish with a light consistency sweep. Commit incrementally.

## Phase Plan

| Phase | Description | Status |
| --- | --- | --- |
| 0 | Create this tracker with rubric, tier model, and status tables | Done |
| 1 | Extend `systems_logic` with the skill tiering and conflict precedence methodology | Done |
| 2 | Add `tier:` frontmatter to all 38 skills; expose tier in `SkillRouter`, `skills.json`, and the AGENTS.md manifest | Done |
| 3 | Self-refine every skill against the rubric, in tier order, committing in batches | Done |
| 4 | Cross-refine overlap clusters; deduplicate content, canonical owner wins | Pending |
| 5 | Final consistency sweep (naming, cross-references, manifest regen) and close out | Pending |

## Refinement Rubric

Every SKILL.md must satisfy all of the following after Phase 3.

### Frontmatter

1. `name` exactly matches the directory name (lowercase, underscores). Known violation: `red_team` declares `"Red Team Cyber Operations"`.
2. `description` is one line, third person, and states both the domain and when the skill should trigger. It is the semantic routing surface, so keywords matter.
3. `triggers` lists 3 to 10 lowercase keywords for deterministic routing. Security skills especially need these (known routing recall gap for `cyber_security` and `blue_team`).
4. `tier` declares the skill's priority tier (0 to 3, defined below).

### Body Structure

5. H1 title, then a one-line scope paragraph or a `## Role` block, then `##`/`###` sections in sequential header order.
6. Bullet style is `-` (several files currently use `*`).
7. Target length 25 to 60 lines. Longer is allowed only when every line is domain-specific.

### Content

8. A skill contains only guidance specific to its domain. Cross-cutting standards (formatting rules, generic input validation, generic testing discipline) live in their canonical owner skill and are referenced, not duplicated.
9. Each skill that depends on another ends with a `## Related Skills` section listing deferrals, for example: `- Defer to \`data_analyst\` for pandas and scikit-learn standards; this skill adds only the sabermetrics deltas.`
10. No per-skill "Formatting Guidelines" boilerplate (trailing whitespace, markdown hierarchy, decorative punctuation rules). That guidance is owned globally by `AGENTS.md` core directives and `architectural_guardrails`.
11. No trailing whitespace; files end with a single newline.

## Tier Model

Assigned in Phase 2 using the `systems_logic` dependency methodology: a skill that other skills inherit standards from sits in a lower (more foundational) tier. Conflict precedence: the lower tier number wins; within the same tier, the more specific skill wins for its own domain.

| Tier | Meaning | Skills |
| --- | --- | --- |
| 0 | Meta and grounding: governs how all other skills are applied | hallucination_guardrails, systems_logic |
| 1 | Core engineering governance: cross-cutting standards domain skills inherit | architectural_guardrails, automation, commit_and_changelog, cyber_security, defensive_debugging, environment_doctor, quality_assurance, software_development, technical_writing, test_and_verify |
| 2 | Technical domain specializations built on Tier 1 | accessibility, blue_team, bug_bounty_hunter, color_theory, data_analyst, database_management, devops, devops_sre, frontend_engineering, google_docs_writer, machine_learning, network_engineering, product_management, red_team, system_administration, ui_ux, visual_design |
| 3 | Application, knowledge, and leisure domains | baseball_analytics, career_assistant, economic_theory, financial_theory, gaming, l4d2_optimization, l4d2_scripting, l4d2_server_management, quantitative_finance |

## Overlap Clusters (Phase 4 scope)

Canonical owner listed first; other members defer and keep only their domain deltas.

| Cluster | Members | Known duplication |
| --- | --- | --- |
| Ops | devops (canonical for CI/CD, containers, IaC ops), devops_sre (refocus on SRE: Terraform/K8s design detail, reliability engineering) | ~80% duplicated sections |
| Security | cyber_security (Tier 1 baseline: zero trust, secrets, PII, logging), red_team, blue_team, bug_bounty_hunter | cyber_security embeds condensed red/blue content; red_team and bug_bounty_hunter share recon/PoC/reporting text |
| Verification | quality_assurance (testing standards and strategy), test_and_verify (operational verification workflow), defensive_debugging (diagnostic protocol), software_development (must drop its embedded verification section) | Same verification principles copied into all four |
| Structure | architectural_guardrails (naming, docs templates, resiliency architecture), software_development (coding practice), technical_writing (documentation authoring) | Naming, ADR/API templates, Mermaid rules duplicated |
| Data/ML | data_analyst (pandas/sklearn/notebook canonical), machine_learning (MLOps deltas), baseball_analytics, quantitative_finance | Pandas wrangling and reproducibility text copied into all four |
| Finance | financial_theory (valuation/risk canonical), quantitative_finance (algorithmic deltas), economic_theory (mostly independent) | Risk metrics and portfolio ratios duplicated |
| Design | ui_ux (UX methodology), accessibility (WCAG canonical), visual_design (layout/typography), color_theory (palettes), frontend_engineering (implementation) | WCAG contrast ratios repeated in four files |
| L4D2 | l4d2_server_management (server ops canonical), l4d2_optimization, l4d2_scripting | Tickrate/rate cvars and edict limits repeated |

## Per-Skill Status

| Skill | Tier | Self-refined (P3) | Cross-refined (P4) | Notes |
| --- | --- | --- | --- | --- |
| hallucination_guardrails | 0 | Done | Pending | drop formatting boilerplate |
| systems_logic | 0 | Done | Pending | extended in P1 |
| architectural_guardrails | 1 | Done | Done | Structure cluster owner |
| automation | 1 | Done | Done | overlaps devops IaC content |
| commit_and_changelog | 1 | Done | Pending | |
| cyber_security | 1 | Done | Done | add triggers; Security cluster owner |
| defensive_debugging | 1 | Done | Done | Verification cluster |
| environment_doctor | 1 | Done | Done | |
| quality_assurance | 1 | Done | Done | Verification cluster owner |
| software_development | 1 | Done | Done | drop embedded verification section |
| technical_writing | 1 | Done | Done | Structure cluster |
| test_and_verify | 1 | Done | Done | Verification cluster |
| accessibility | 2 | Done | Pending | Design cluster WCAG owner |
| blue_team | 2 | Done | Done | add triggers |
| bug_bounty_hunter | 2 | Done | Done | Security cluster |
| color_theory | 2 | Done | Pending | Design cluster |
| data_analyst | 2 | Done | Done | Data/ML cluster owner |
| database_management | 2 | Done | Pending | |
| devops | 2 | Done | Done | Ops cluster owner |
| devops_sre | 2 | Done | Done | refocus on SRE deltas |
| frontend_engineering | 2 | Done | Pending | Design cluster |
| google_docs_writer | 2 | Done | Pending | |
| machine_learning | 2 | Done | Done | Data/ML cluster |
| network_engineering | 2 | Done | Done | overlaps devops_sre network section |
| product_management | 2 | Done | Pending | shortest skill; may expand slightly |
| red_team | 2 | Done | Done | fix frontmatter name |
| system_administration | 2 | Done | Done | |
| ui_ux | 2 | Done | Pending | Design cluster |
| visual_design | 2 | Done | Pending | Design cluster |
| baseball_analytics | 3 | Done | Done | defers to data_analyst |
| career_assistant | 3 | Done | Pending | grounded in USER_PROFILE.md |
| economic_theory | 3 | Done | Done | Finance cluster |
| financial_theory | 3 | Done | Done | Finance cluster owner |
| gaming | 3 | Done | Pending | |
| l4d2_optimization | 3 | Done | Pending | L4D2 cluster |
| l4d2_scripting | 3 | Done | Pending | L4D2 cluster |
| l4d2_server_management | 3 | Done | Pending | L4D2 cluster owner |
| quantitative_finance | 3 | Done | Done | Data/ML and Finance clusters |

## Operational Notes

- The pre-commit hook regenerates `skills.json` and the AGENTS.md manifest table automatically; never hand-edit those.
- `tier:` frontmatter here means priority/conflict precedence. The payload pipeline's pass-affinity concept from `improvements.md` should use a distinct key (for example `pipeline_pass:`) when implemented, to avoid colliding semantics.
- Commit format per `commit_and_changelog`: `<type>(<scope>): <description>`, no dashes as dividers.
- Do not commit `.telemetry/telemetry.db` or `build/lib/**` churn with these changes; stage skill and doc files explicitly.
- On completion, update `improvements.md`: the "tier frontmatter for skills" and "close the skill routing recall gap for security prompts" items are satisfied by this effort.
