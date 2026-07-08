#!/usr/bin/env python3
"""
Project Scaffolding Utility
"""

import os


class ProjectScaffolder:
    """Class to handle project scaffolding."""

    def __init__(self, project_name: str, project_type: str):
        """Initializes the scaffolder with project details."""
        self.project_name = project_name
        self.project_type = project_type

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.repo_root = os.path.dirname(script_dir)
        self.target_dir = os.path.join(self.repo_root, "projects", self.project_name)

    def _create_file(self, path: str, content: str) -> None:
        """Helper to create a file with specific content."""
        with open(path, "w") as f:
            f.write(content)

    def generate(self) -> None:
        """Generates the project structure."""
        os.makedirs(self.target_dir, exist_ok=True)

        self._create_file(
            os.path.join(self.target_dir, "README.md"),
            f"# {self.project_name}\n\nProject initialized automatically.",
        )

        if self.project_type == "python":
            self._scaffold_python()
        elif self.project_type == "go":
            self._scaffold_go()
        else:
            print("Unknown project type.")

    def _scaffold_python(self) -> None:
        """Generates Python specific files and directories."""
        os.makedirs(os.path.join(self.target_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(self.target_dir, "src"), exist_ok=True)
        self._create_file(os.path.join(self.target_dir, "requirements.txt"), "")
        self._create_file(
            os.path.join(self.target_dir, "main.py"), "print('Hello World')\n"
        )
        print(f"Python project scaffolded rapidly at {self.target_dir}")

    def _scaffold_go(self) -> None:
        """Generates Go specific files."""
        self._create_file(
            os.path.join(self.target_dir, "main.go"),
            'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello World")\n}\n',
        )
        print(f"Go project scaffolded rapidly at {self.target_dir}")


def main():
    """Main entry point."""
    print("Welcome to the AI Project Scaffolding Utility")
    project_name = input("Enter project name: ").strip()
    project_type = input("Language (python or go): ").strip().lower()

    scaffolder = ProjectScaffolder(project_name, project_type)
    scaffolder.generate()


if __name__ == "__main__":
    main()
