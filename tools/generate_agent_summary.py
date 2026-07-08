#!/usr/bin/env python3
import os
import urllib.request
import json


def fetch_github_data(username):
    url = f"https://api.github.com/users/{username}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf8"))
                return data.get("public_repos", 0), data.get("bio", "")
    except Exception:
        pass
    return None, None


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    summary_path = os.path.join(repo_root, ".agents", "rules", "user_summary.md")

    repos, bio = fetch_github_data("howlcipher")

    summary = [
        "---\n",
        "name: user_summary\n",
        "description: Condensed user profile for quick context injection.\n",
        "---\n",
        "User is William Elias, a Software Engineer specializing in Cyber Defense.\n",
        "Core capabilities include Python, Go, Docker, and secure Cloud architecture.\n",
    ]

    if repos is not None:
        summary.append(f"Live GitHub Stats: {repos} public repositories.\n")
    if bio:
        summary.append(f"Live GitHub Bio: {bio}\n")

    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w") as f:
        f.writelines(summary)

    print(
        "Agent summary generated with dynamic API data at .agents/rules/user_summary.md"
    )


if __name__ == "__main__":
    main()
