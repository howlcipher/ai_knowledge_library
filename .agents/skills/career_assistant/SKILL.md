---
name: "career_assistant"
description: "Explicit guidelines and procedures for assisting the user with job applications, tailoring resumes, writing cover letters, and personal branding."
triggers:
  - "resume"
  - "cover letter"
  - "job application"
  - "interview"
  - "personal branding"
tier: 3
---

# Career Assistant Guidelines

This skill defines the operational framework and procedures for assisting users with professional growth and application processes, including resume customization, cover letter composition, and interview preparation.

## Core Directives

### 1. Profile Grounding
- Before generating any personal or professional content, you must read the `USER_PROFILE.md` file located in the workspace root directory.
- Ground all generated claims, achievements, and technical expertise strictly in the verified profile data.

### 2. Tone and Professional Identity
- Maintain a tone that is professional, confident, and authentic to the user's career level.
- Emphasize the user's primary engineering strengths (e.g., software engineering, quality assurance, system administration, and infrastructure automation).

### 3. Verification and Integrity
- Do not fabricate or estimate skills, job titles, tenures, or project details.
- If the target job description requires a skill not present in the user profile, highlight transferable skills or flag the gap for the user rather than inventing experience.

### 4. Experience Filtering and Targeting
- Analyze target job descriptions to identify key requirements, technologies, and methodologies.
- Prioritize and highlight matching skills from the user profile, while filtering out or deprioritizing unrelated historical details.

## Standard Workflows

### 1. Resume Tailoring
- **Input Requirements:** Target job description and current user profile.
- **Analysis:** Extract primary keywords, technologies, and core responsibilities from the job description. Cross-reference with the user's historical experience.
- **Execution:** Refine specific bullet points to map closely to target keywords while preserving the veracity of the original accomplishments.

### 2. Cover Letter Generation
- **Input Requirements:** Target role, company background, and user profile.
- **Analysis:** Identify the company's technical pain points and cultural values.
- **Execution:** Synthesize a compelling narrative showing how the user's specific achievements (such as zero-downtime migrations, automation pipelines, or QA test suites) directly solve the target company's challenges. Keep the output concise and highly customized.

### 3. Interview Preparation
- **Input Requirements:** Target job description or specific technical domain.
- **Analysis:** Determine typical behavioral, system design, and coding questions for the role.
- **Execution:** Provide a curated list of questions accompanied by structured talking points mapped directly to the user's documented projects and achievements.
