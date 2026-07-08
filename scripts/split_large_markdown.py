#!/usr/bin/env python3
"""
Utility to split large markdown files into smaller chunks.
"""

import os
import math


class MarkdownSplitter:
    """Class to handle finding and splitting large markdown files."""

    def __init__(self, max_lines: int = 500, exclude_files: list = None):
        """Initializes the splitter."""
        self.max_lines = max_lines
        self.exclude_files = exclude_files or [
            "README.md",
            "change_log.md",
            "GEMINI.md",
            "USER_PROFILE.md",
        ]

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.repo_root = os.path.dirname(script_dir)

    def split_file(self, filepath: str) -> bool:
        """Splits a single markdown file if it exceeds the max lines threshold."""
        with open(filepath, "r", encoding="utf8") as f:
            lines = f.readlines()

        if len(lines) <= self.max_lines:
            return False

        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        num_parts = math.ceil(len(lines) / self.max_lines)
        for i in range(num_parts):
            part_lines = lines[i * self.max_lines : (i + 1) * self.max_lines]
            part_name = f"{name}_part{i + 1}{ext}"
            part_path = os.path.join(directory, part_name)

            with open(part_path, "w", encoding="utf8") as f:
                f.writelines(part_lines)

        os.remove(filepath)
        print(f"Split {filename} into {num_parts} optimized chunks.")
        return True

    def scan_and_split(self) -> None:
        """Scans the repository and splits oversized markdown files."""
        print("Scanning library for oversized markdown files...")
        for root, dirs, files in os.walk(self.repo_root):
            if ".git" in root or ".agents" in root:
                continue
            for file in files:
                if file.endswith(".md") and file not in self.exclude_files:
                    filepath = os.path.join(root, file)
                    self.split_file(filepath)


def split_file(filepath: str, max_lines: int = 500) -> bool:
    """Legacy function to maintain exact compatibility."""
    splitter = MarkdownSplitter(max_lines=max_lines)
    return splitter.split_file(filepath)


def main():
    """Main entry point."""
    splitter = MarkdownSplitter()
    splitter.scan_and_split()


if __name__ == "__main__":
    main()
