#!/usr/bin/env python3
"""
Library Search Tool (Brain).

This module provides an object oriented search functionality across the
library files. It respects configuration for excluded directories
and file extensions.
"""

import os
import sys

# Ensure repo root is in sys.path to import from config
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, ".."))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from src.infrastructure.config_loader import load_config


class LibrarySearcher:
    """
    Handles searching for specific terms within the library files.
    """

    def __init__(self, search_term: str):
        """
        Initializes the LibrarySearcher with a search term and loads configuration.

        Args:
            search_term (str): The term to search for.
        """
        self.search_term = search_term.lower()
        self.repo_root = repo_root

        # Load configuration for exclusions and extensions
        self.config = load_config().get("search", {})
        self.exclude_dirs = self.config.get("exclude_dirs", [".git", ".agents"])
        self.file_extensions = self.config.get("file_extensions", [".md"])

    def _should_exclude_dir(self, directory: str) -> bool:
        """
        Checks if a directory should be excluded from the search.

        Args:
            directory (str): Directory path or name.

        Returns:
            bool: True if the directory should be excluded, False otherwise.
        """
        for exclude in self.exclude_dirs:
            if exclude in directory:
                return True
        return False

    def search(self):
        """
        Executes the search across the repository.
        Prints out the matches found, showing relative file path and line number.
        """
        print(f"Searching library for: {self.search_term}")
        found = False

        for root, dirs, files in os.walk(self.repo_root):
            if self._should_exclude_dir(root):
                continue

            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    if self._search_in_file(root, file):
                        found = True

        if not found:
            print("No results found.")

    def _search_in_file(self, root: str, file: str) -> bool:
        """
        Searches for the term within a specific file.

        Args:
            root (str): The directory containing the file.
            file (str): The file name.

        Returns:
            bool: True if matches were found, False otherwise.
        """
        filepath = os.path.join(root, file)
        found = False
        try:
            with open(filepath, "r", encoding="utf8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if self.search_term in line.lower():
                        rel_path = os.path.relpath(filepath, self.repo_root)
                        print(f"[{rel_path} Line {i + 1}] {line.strip()}")
                        found = True
        except Exception:
            pass

        return found


def main():
    """
    Main entry point for the search script.
    """
    if len(sys.argv) < 2:
        print("Usage: python3 src/core/brain.py <search_term>")
        return

    term = sys.argv[1]
    searcher = LibrarySearcher(term)
    searcher.search()


if __name__ == "__main__":
    main()
