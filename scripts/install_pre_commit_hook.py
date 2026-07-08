#!/usr/bin/env python3
import os


def main():
    hook_dir = ".git/hooks"
    os.makedirs(hook_dir, exist_ok=True)
    hook_path = os.path.join(hook_dir, "pre-commit")

    content = """#!/usr/bin/env bash
if git diff --cached --name-only | grep -q ".env"; then
    echo "ERROR: Attempting to commit a .env file. Commit aborted."
    exit 1
fi
"""
    with open(hook_path, "w") as f:
        f.write(content)
    os.chmod(hook_path, 0o755)  # nosec B103
    print("Pre-commit hook installed successfully.")


if __name__ == "__main__":
    main()
