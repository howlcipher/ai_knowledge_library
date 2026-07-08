#!/usr/bin/env python3
import os


def create_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def main():
    print("Welcome to the AI Project Scaffolding Utility")
    project_name = input("Enter project name: ").strip()
    project_type = input("Language (python or go): ").strip().lower()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    target_dir = os.path.join(repo_root, "projects", project_name)

    os.makedirs(target_dir, exist_ok=True)

    create_file(
        os.path.join(target_dir, "README.md"),
        f"# {project_name}\n\nProject initialized automatically.",
    )

    if project_type == "python":
        os.makedirs(os.path.join(target_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(target_dir, "src"), exist_ok=True)
        create_file(os.path.join(target_dir, "requirements.txt"), "")
        create_file(os.path.join(target_dir, "main.py"), "print('Hello World')\n")
        print(f"Python project scaffolded rapidly at {target_dir}")
    elif project_type == "go":
        create_file(
            os.path.join(target_dir, "main.go"),
            'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello World")\n}\n',
        )
        print(f"Go project scaffolded rapidly at {target_dir}")
    else:
        print("Unknown project type.")


if __name__ == "__main__":
    main()
