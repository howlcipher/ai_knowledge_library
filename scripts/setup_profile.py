#!/usr/bin/env python3
"""
Profile Setup Script

This script assists in setting up or modifying a user profile markdown file
used across the AI Knowledge Library.
"""

import os
from typing import Tuple


class ProfileManager:
    """Handles the creation and management of user profiles."""

    def __init__(self, repo_root: str):
        """
        Initialize the ProfileManager.

        Args:
            repo_root (str): The root directory of the repository.
        """
        self.repo_root = repo_root
        self.default_profile = os.path.join(repo_root, "USER_PROFILE.md")

    def prompt_user_details(self) -> Tuple[str, str, str, str]:
        """Prompt user for their profile details."""
        print("Please enter the details for the new profile.")
        name = input("Full Name: ").strip()
        email = input("Email: ").strip()
        linkedin = input("LinkedIn URL (optional): ").strip()
        github = input("GitHub Username (optional): ").strip()
        return name, email, linkedin, github

    def _generate_content(
        self, name: str, email: str, linkedin: str, github: str
    ) -> str:
        """Generate the markdown content for a user profile."""
        content = [
            f"# {name} User Profile\n",
            "## Contact and Links",
            f"* Email: {email}",
        ]

        if linkedin:
            content.append(f"* LinkedIn: {linkedin}")
        if github:
            content.append(f"* GitHub: github.com/{github}")

        content.extend(
            [
                "",
                "## Professional Summary",
                "Add your professional summary here.",
                "",
                "## Core Skills",
                "* Add your core skills here.",
                "",
                "## Professional Experience",
                "* Add your experience here.",
                "",
                "## Education and Certifications",
                "* Add your education here.",
            ]
        )

        return "\n".join(content) + "\n"

    def write_profile(self, path: str, content: str):
        """Write the generated profile content to a file."""
        with open(path, "w") as f:
            f.write(content)

    def create_secondary_profile(self):
        """Create a new profile without removing the default one."""
        name, email, linkedin, github = self.prompt_user_details()
        safe_name = name.replace(" ", "_").lower()
        new_profile_path = os.path.join(self.repo_root, f"USER_PROFILE_{safe_name}.md")

        content = self._generate_content(name, email, linkedin, github)
        self.write_profile(new_profile_path, content)

        print(f"Created new profile at USER_PROFILE_{safe_name}.md")
        print("Original profile kept intact.")

    def replace_primary_profile(self):
        """Remove the default profile and create a new primary profile."""
        name, email, linkedin, github = self.prompt_user_details()

        if os.path.exists(self.default_profile):
            os.remove(self.default_profile)
            print("Removed default USER_PROFILE.md")

        content = self._generate_content(name, email, linkedin, github)
        self.write_profile(self.default_profile, content)

        print(f"Created your new primary profile at USER_PROFILE.md")


def main():
    """Main execution point for profile setup."""
    print("Welcome to the AI Knowledge Library Profile Setup")
    print("1. Keep the original William Elias profile and add a new one.")
    print("2. Remove the William Elias profile entirely and create your own.")
    print("3. Exit without making changes.")

    choice = input("Enter your choice (1, 2, or 3): ").strip()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    manager = ProfileManager(repo_root)

    if choice == "1":
        manager.create_secondary_profile()
    elif choice == "2":
        manager.replace_primary_profile()
    else:
        print("Exiting without changes.")


if __name__ == "__main__":
    main()
