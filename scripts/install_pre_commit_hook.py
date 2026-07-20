#!/usr/bin/env python3
import os


def main():
    hook_dir = ".git/hooks"
    os.makedirs(hook_dir, exist_ok=True)
    hook_path = os.path.join(hook_dir, "pre-commit")

    content = """#!/usr/bin/env bash
if git diff --cached --name-only | grep -qE '(^|/)\\.env(\\.|$)'; then
    echo "ERROR: Attempting to commit a .env file. Commit aborted."
    exit 1
fi

# Regenerate the skills manifest (AGENTS.md), index (.agents/skills.json),
# and the .claude/skills/ symlink set when any skill or command-skill
# definition is part of the commit.
if git diff --cached --name-only | grep -qE "^\\.agents/(skills|skill_commands)/"; then
    echo "Skill files changed; regenerating skills manifest and index..."
    if python3 scripts/generate_skills_manifest.py; then
        git add AGENTS.md .agents/skills.json .claude/skills
    else
        echo "ERROR: skills manifest regeneration failed. Commit aborted."
        exit 1
    fi
fi
"""
    with open(hook_path, "w") as f:
        f.write(content)
    os.chmod(hook_path, 0o755)  # nosec B103
    print("Pre-commit hook installed successfully.")


if __name__ == "__main__":
    main()
