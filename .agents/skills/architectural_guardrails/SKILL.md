name: "architectural_guardrails"
description: "Triggers during project initialization, layout mapping, or structural documentation routines"

# Global Architectural Standards

## Style Rules
* Do not use dashes or subtraction symbols as punctuation under any circumstances. Use underscores for file names and spaces for standard text.
* Present complex data using clean Markdown tables.
* Keep summaries extremely concise.

## Execution Resiliency
* Ensure all asynchronous background processes implement non blocking execution logic.
* Every error handling routine must emit a structured log payload detailing the exact failure vector.\n