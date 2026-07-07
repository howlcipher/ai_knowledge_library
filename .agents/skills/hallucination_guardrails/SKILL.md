name: "hallucination_guardrails"
description: "Triggers continuously across all active prompts to ground agent reasoning"

# Reality Validation Rules

## The Source Verification Law
* Never guess whether a file or path exists. You must explicitly search or read the folder workspace first.
* Rely exclusively on the code patterns and configuration schemas present within the active tracking tree.

## Boundary Enforcement
* If context is missing, stop execution immediately and explain the gap clearly.
* State clearly that you do not know the answer rather than generating speculative placeholder code.
* Do not rewrite code components outside the explicit scope requested.\n