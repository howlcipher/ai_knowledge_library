#!/usr/bin/env python3
import os
import stat

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    hook_path = os.path.join(repo_root, ".git", "hooks", "pre-commit")
    
    hook_content = """#!/usr/bin/env bash
echo 'Running dead link scanner'
python3 tools/check_dead_links.py
if [ $? -ne 0 ]; then
  echo 'Dead links found. Commit aborted.'
  exit 1
fi
"""
    with open(hook_path, "w") as f:
        f.write(hook_content)
    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IEXEC)
    print("Pre-commit hook installed successfully.")

if __name__ == "__main__":
    main()
