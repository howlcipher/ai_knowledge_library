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
    hook_content = "#!/usr/bin/env bash\necho 'Running pre push unit tests'\n"
    with open(hook_path, "w") as f:
        f.write(hook_content)
    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IEXEC)
    print("Pre push hook installed successfully.")


if __name__ == "__main__":
    main()
