# Future Automation and Feature Backlog

1. **Local RAG & Vector Database**: Integrate `chromadb` or `faiss` in the `tools/` directory to create a semantic search index of the entire library, allowing the AI to rapidly recall related ADRs, skills, and rules without doing massive text scans.
2. **Automated API Documentation**: Implement a GitHub Action utilizing `pdoc` or `Sphinx` that automatically generates and publishes static documentation for the `tools/` and `scripts/` directories to a `gh-pages` branch.
3. **Data Science & ML Skill**: Create `.agents/skills/data_analyst/SKILL.md` to equip the AI with explicit methodologies for pandas, jupyter data wrangling, and scikit-learn ML pipelines.
4. **Taskfile/Make Standardization**: Introduce a global `Taskfile.yml` or `Makefile` to centralize all test running, linting, and building commands into a single standard tool across Python and Go ecosystems.
