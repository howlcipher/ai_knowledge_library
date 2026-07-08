#!/usr/bin/env python3
"""
Template Injector Script

This script dynamically injects user profile variables into
agent skill templates using Jinja2.
"""

import os
import re
from jinja2 import Environment


class ProfileInjector:
    """Handles injecting profile variables into SKILL.md templates."""

    def __init__(self, repo_root: str):
        """
        Initialize the ProfileInjector.

        Args:
            repo_root (str): The root directory of the repository.
        """
        self.repo_root = repo_root
        self.profile_path = os.path.join(repo_root, "USER_PROFILE.md")
        self.skills_dir = os.path.join(repo_root, ".agents", "skills")
        self.env = Environment(autoescape=True)

    def _read_profile(self) -> str:
        """Read the profile content if it exists."""
        if not os.path.exists(self.profile_path):
            return None
        with open(self.profile_path, "r") as f:
            return f.read()

    def _extract_user_name(self, profile_content: str) -> str:
        """Extract the user's name from the profile markdown."""
        name_match = re.search(r"# (.+) User Profile", profile_content)
        return name_match.group(1) if name_match else "User"

    def inject(self):
        """Perform the template injection process."""
        profile_content = self._read_profile()
        if not profile_content:
            print("USER_PROFILE.md not found. Skipping dynamic templating.")
            return

        user_name = self._extract_user_name(profile_content)
        context = {"USER_NAME": user_name, "PROFILE": profile_content}

        self._process_skills(context)

        print(
            "Dynamically injected USER_PROFILE.md variables into SKILL.md templates using Jinja2."
        )

    def _process_skills(self, context: dict):
        """Walk the skills directory and apply templates."""
        if not os.path.exists(self.skills_dir):
            return

        for root, _, files in os.walk(self.skills_dir):
            for file in files:
                if file == "SKILL.md":
                    self._render_template_file(os.path.join(root, file), context)

    def _render_template_file(self, path: str, context: dict):
        """Render a single template file and save it."""
        with open(path, "r") as f:
            content = f.read()

        if "{{" in content and "}}" in content:
            template = self.env.from_string(content)
            rendered = template.render(**context)
            with open(path, "w") as f:
                f.write(rendered)


def main():
    """Main execution point for the template injector script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    injector = ProfileInjector(repo_root)
    injector.inject()


if __name__ == "__main__":
    main()
