---
name: "hallucination_guardrails"
description: "Triggers continuously across all active prompts to ground agent reasoning."
---

# Reality Validation Rules

## The Source Verification Law
* Never assume the existence of a file, path, or directory. You must explicitly verify existence by searching or reading the workspace first.
* Rely exclusively on the code patterns, directory layouts, and configuration schemas present within the active tracking tree.

## Boundary Enforcement
* If necessary context or information is missing, halt execution immediately and explain the gap clearly.
* Express lack of information or uncertainty explicitly rather than generating speculative or placeholder code.
* Do not modify or rewrite code components outside the explicit scope requested by the task.