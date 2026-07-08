#!/usr/bin/env python3
"""
Module for generating library statistics and updating the README with a badge.
"""

import os
import re


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
        self.badge_pattern = r'<img src="https://img\.shields\.io/static/v1\?label=Library_Size&message=\d+&color=success&style=for_the_badge" alt="Library Size Badge" />'
        self.first_badge_line = '<img src="https://img.shields.io/static/v1?label=AI&message=Knowledge_Library&color=blueviolet&style=for_the_badge" alt="AI Library Badge" />'

    def count_files(self) -> int:
        """
        Counts the number of files in the repository, excluding '.git' directories.

        Returns:
            int: The total number of files.
        """
        file_count = 0
        for root, _, files in os.walk(self.repo_root):
            if ".git" in root:
                continue
            file_count += len(files)
        return file_count

    def update_readme(self, file_count: int) -> None:
        """
        Updates the README.md file with the new file count badge.

        Args:
            file_count (int): The number of files to display in the badge.
        """
        if not os.path.exists(self.readme_path):
            print(f"README not found at {self.readme_path}")
            return

        with open(self.readme_path, "r") as f:
            content = f.read()

        new_badge = f'<img src="https://img.shields.io/static/v1?label=Library_Size&message={file_count}&color=success&style=for_the_badge" alt="Library Size Badge" />'

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
        file_count = self.count_files()
        self.update_readme(file_count)
        print(
            f"Library statistics generated: {file_count} files counted. README updated."
        )


def main():
    """
    Main entry point for the script.
    """
    generator = LibraryStatisticsGenerator()
    generator.run()


if __name__ == "__main__":
    main()
