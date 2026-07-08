#!/usr/bin/env python3
"""
Dead Link Checker Tool.

This module provides an object oriented tool to scan markdown files
in the repository for dead local links.
"""

import os
import re
import sys

# Ensure repo root is in sys.path to import from config
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, ".."))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from config.loader import load_config


class DeadLinkChecker:
    """
    Scans the repository for broken local markdown links.
    """

    def __init__(self):
        """
        Initializes the DeadLinkChecker and loads configuration.
        """
        self.repo_root = repo_root

        # Load configurations for exclusions and extensions
        self.config = load_config().get("link_checker", {})
        self.exclude_dirs = self.config.get("exclude_dirs", [".git"])
        self.file_extensions = self.config.get("file_extensions", [".md"])

        # Regex to find all markdown links
        self.link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

        self.has_dead_links = False

    def _should_exclude_dir(self, directory: str) -> bool:
        """
        Checks if a directory should be excluded from checking.

        Args:
            directory (str): Directory path or name.

        Returns:
            bool: True if excluded, False otherwise.
        """
        for exclude in self.exclude_dirs:
            if exclude in directory:
                return True
        return False

    def _is_external_or_special_link(self, link: str) -> bool:
        """
        Determines if a link is an external URL, anchor, or email.

        Args:
            link (str): The link URL or path.

        Returns:
            bool: True if the link is external or special, False if it is a local file.
        """
        return (
            link.startswith("http")
            or link.startswith("#")
            or link.startswith("mailto:")
        )

    def _check_file_links(self, file_path: str, root: str):
        """
        Checks all links in a given markdown file.

        Args:
            file_path (str): The absolute path to the file.
            root (str): The directory containing the file.
        """
        with open(file_path, "r", encoding="utf8") as f:
            content = f.read()

        links = self.link_pattern.findall(content)
        for text, link in links:
            if not self._is_external_or_special_link(link):
                target_path = os.path.normpath(os.path.join(root, link.split("#")[0]))
                if not os.path.exists(target_path):
                    print(f"Dead link found in {file_path}: {link}")
                    self.has_dead_links = True

    def run(self) -> bool:
        """
        Executes the dead link scanning process across the repository.

        Returns:
            bool: True if dead links were found, False otherwise.
        """
        for root, _, files in os.walk(self.repo_root):
            if self._should_exclude_dir(root):
                continue

            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    file_path = os.path.join(root, file)
                    self._check_file_links(file_path, root)

        return self.has_dead_links


def main():
    """
    Main entry point for the dead link checking script.
    """
    checker = DeadLinkChecker()
    found_dead_links = checker.run()

    if found_dead_links:
        sys.exit(1)

    print("No dead links found.")
    sys.exit(0)


if __name__ == "__main__":
    main()
