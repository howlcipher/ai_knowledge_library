#!/usr/bin/env python3
"""
Module for generating library statistics and updating the README with a badge.
"""

import os
import re
import json


class LibraryStatisticsGenerator:
    """
    Handles calculating library statistics and updating the repository README.
    """

    def __init__(self, repo_root: str = None):
        """
        Initializes the LibraryStatisticsGenerator.

        Args:
            repo_root (str, optional): The root directory of the repository.
                Defaults to the parent directory of this script's location.
        """
        if repo_root is None:
            self.repo_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..")
            )
        else:
            self.repo_root = repo_root

        self.readme_path = os.path.join(self.repo_root, "README.md")
        self.badge_pattern = r'<img src="https://img\.shields\.io/static/v1\?label=Neural_Nodes&message=\d+&color=00ff41&style=for_the_badge" alt="Neural Nodes Badge" />'
        self.first_badge_line = '<img src="https://img.shields.io/static/v1?label=SYS_CORE&message=Active&color=00f0ff&style=for_the_badge" alt="AI Library Badge" />'
        # Path to the skills manifest JSON file
        self.skills_manifest_path = os.path.join(self.repo_root, ".agents", "skills.json")

    def count_skills(self) -> int:
        """Counts the number of skills declared in the skills manifest."""
        with open(self.skills_manifest_path, "r") as f:
            manifest = json.load(f)
        return len(manifest["skills"])

    def update_readme(self, skill_count: int) -> None:
        """
        Updates the README.md file with the new skill count badge.

        Args:
            skill_count (int): The number of skills to display in the badge.
        """
        if not os.path.exists(self.readme_path):
            print(f"README not found at {self.readme_path}")
            return

        with open(self.readme_path, "r") as f:
            content = f.read()

        new_badge = f'<img src="https://img.shields.io/static/v1?label=Neural_Nodes&message={skill_count}&color=00ff41&style=for_the_badge" alt="Neural Nodes Badge" />'

        if re.search(self.badge_pattern, content):
            content = re.sub(self.badge_pattern, new_badge, content)
        else:
            # Insert after the first badge line
            content = content.replace(
                self.first_badge_line, f"{self.first_badge_line}\n  {new_badge}"
            )

        with open(self.readme_path, "w") as f:
            f.write(content)

    def run(self) -> None:
        """
        Executes the statistics generation and README update process.
        """
        skill_count = self.count_skills()
        self.update_readme(skill_count)
        print(
            f"Library statistics generated: {skill_count} skills counted. README updated."
        )


def main():
    """
    Main entry point for the script.
    """
    generator = LibraryStatisticsGenerator()
    generator.run()


if __name__ == "__main__":
    main()
