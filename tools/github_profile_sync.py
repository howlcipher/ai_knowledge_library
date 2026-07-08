#!/usr/bin/env python3
import urllib.request
import json
import os
import sys


def fetch_github_repos(username):
    url = f"https://api.github.com/users/{username}/repos?sort=updated"
    req = urllib.request.Request(url, headers={"User-Agent": "KnowledgeLibrary_Sync"})
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data
    except Exception as e:
        print(f"Error fetching data: {e}")
    return []


def main():
    username = "howlcipher"
    print(f"Fetching recent repositories for {username}...")
    repos = fetch_github_repos(username)

    if not repos:
        print("No repositories found or sync failed.")
        sys.exit(1)

    output_lines = ["\n## Recent GitHub Projects\n"]
    for repo in repos[:5]:
        name = repo.get("name", "Unknown")
        desc = repo.get("description", "No description provided.")
        if desc is None:
            desc = "No description provided."
        url = repo.get("html_url", "")
        # Remove hyphens/dashes from descriptions to comply with formatting rules!
        desc = desc.replace("-", " ")
        output_lines.append(f"* **{name}**: {desc} ({url})")

    profile_path = os.path.join(os.path.dirname(__file__), "..", "USER_PROFILE.md")

    if os.path.exists(profile_path):
        with open(profile_path, "a") as f:
            f.write("\n" + "\n".join(output_lines) + "\n")
        print("Successfully synced GitHub projects to USER_PROFILE.md.")
    else:
        print("USER_PROFILE.md not found.")


if __name__ == "__main__":
    main()
