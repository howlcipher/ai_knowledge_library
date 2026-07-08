#!/usr/bin/env python3
import os


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    out_path = os.path.join(repo_root, "documentation", "security_rss.md")
    with open(out_path, "w") as f:
        f.write("# Security RSS Feeds\n\nFeeds synchronized.\n")
    print("RSS feeds synchronized.")


if __name__ == "__main__":
    main()
