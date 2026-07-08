#!/usr/bin/env python3
import os
import re
import sys


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    has_dead_links = False

    for root, _, files in os.walk(repo_root):
        if ".git" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find all markdown links
                links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
                for text, link in links:
                    if (
                        not link.startswith("http")
                        and not link.startswith("#")
                        and not link.startswith("mailto:")
                    ):
                        # check if local file exists
                        # link can be relative or absolute from repo root
                        target_path = os.path.normpath(
                            os.path.join(root, link.split("#")[0])
                        )
                        if not os.path.exists(target_path):
                            print(f"Dead link found in {file_path}: {link}")
                            has_dead_links = True

    if has_dead_links:
        sys.exit(1)
    print("No dead links found.")
    sys.exit(0)


if __name__ == "__main__":
    main()
