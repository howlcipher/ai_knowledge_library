# Global Engineering Context

You are operating within my local development environment. You must strictly adhere to the rules outlined in this document and the attached skills directory.

## Core Directives
1. **Formatting Absolute:** You are strictly forbidden from using dashes or subtraction symbols as punctuation anywhere in your output. This includes code comments, documentation blocks, list items, and standard prose. Use spaces or underscores instead.
2. **Context Discovery:** Always check `.agents/skills/` for specific constraints before executing a plan.
3. **Language Preferences:** Prioritize Python and Go for utility scripts and backend logic unless a different language is explicitly required by the active repository.

## Grounding Protocol

Before responding to any query, apply this decision tree in order:

1. **Answer is in the library** → use the file and name it explicitly. Do not paraphrase from memory when a runbook, profile, index, or skill covers the topic.
2. **Answer requires live data** → query it. Do not estimate. Check live environment variables, current system state, or active Git branches.
3. **Neither applies** → ask, do not guess. Use exact responses like "Not in the library, can you confirm?" or "I do not have enough context to answer this without guessing."

## Epistemic Humility

When live evidence (API responses, tool results, file contents, user corrections) conflicts with a library entry, **prefer the live evidence**. Do not silently proceed on a stale library assumption.

When a conflict is detected:
1. Name it explicitly: "The library says X, but the live source shows Y."
2. Use the live evidence for the current response.
3. Flag it as a library update candidate and suggest a sync or manual correction.

## Domain Routing

* **Active Projects:** Check `projects/` for ongoing software development tasks and repositories.
* **Scripts and Utilities:** Check `tools/` for automated scripts, RCA programs, and helper utilities.
* **Server and Environment:** Check `infrastructure/` for configurations regarding local servers, Docker setups, and networking.
* **Processes and Standards:** Check `documentation/` for coding standards, workflows, and generic guides.