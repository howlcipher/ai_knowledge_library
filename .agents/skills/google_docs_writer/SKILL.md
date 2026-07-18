---
name: "google_docs_writer"
description: "Triggers when assisting with drafting, formatting, or integrating content for Google Docs."
triggers:
  - "google docs"
  - "docs formatting"
tier: 2
---

# Google Docs Writing Methodologies

## Security and Privacy
- Never store personal Google Docs links, authorization tokens, or Workspace URLs directly in the repository text.
- Always instruct the AI to read the user's personal Google Docs URLs from their local, securely ignored `.env` file via the `GOOGLE_DOCS_WORKSPACE_URL` variable.

## Content Structuring and Writing Standards
- Draft all documentation in standard Markdown format locally first, ensuring it perfectly translates to Google Docs styling when copied over.
- Write in a direct, active voice with high clarity and precision, avoiding unnecessary jargon and hand-waving explanations.
- Utilize a sequential structured hierarchy (H1 to H6) and clear bullet points to ensure maximum readability in collaborative environments.
- When executing technical writing, always construct an executive summary at the top before diving into the complex architecture.
- Apply standardized templates for documents like API Specifications or Architecture Decision Records (ADRs). Ensure any embedded workflows or state transitions are visualized with valid Mermaid.js diagrams.

## Documentation Enforcement and Formatting
- Ensure that the project's root `README.md` and `change_log.md` are updated to reflect any documentation additions before making git commits.
