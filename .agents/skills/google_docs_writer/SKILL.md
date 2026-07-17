---
name: "google_docs_writer"
description: "Triggers when assisting with drafting, formatting, or integrating content for Google Docs."
---

# Google Docs Writing Methodologies

## Security and Privacy
* Never store personal Google Docs links, authorization tokens, or Workspace URLs directly in the repository text.
* Always instruct the AI to read the user's personal Google Docs URLs from their local, securely ignored `.env` file via the `GOOGLE_DOCS_WORKSPACE_URL` variable.

## Content Structuring
* Draft all documentation in standard Markdown format locally first, ensuring it perfectly translates to Google Docs styling when copied over.
* Utilize clear headings, bullet points, and concise professional language to ensure maximum readability in collaborative environments.
* When executing technical writing, always construct an executive summary at the top before diving into the complex architecture.
