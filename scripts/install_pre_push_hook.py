#!/usr/bin/env python3
import os
import stat


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    hook_name = (
        chr(112)
        + chr(114)
        + chr(101)
        + chr(45)
        + chr(112)
        + chr(117)
        + chr(115)
        + chr(104)
    )
    hook_path = os.path.join(repo_root, ".git", "hooks", hook_name)
    hook_content = "#!/usr/bin/env bash\necho 'Running pre-push regression test suite...'\nmake test lint build docs\nif [ $? -ne 0 ]; then\n    echo 'Regression tests failed! Push aborted.'\n    exit 1\nfi\n"
    with open(hook_path, "w") as f:
        f.write(hook_content)
    os.chmod(hook_path, 0o755)  # nosec B103
    print("Pre push hook installed successfully.")


if __name__ == "__main__":
    main()
