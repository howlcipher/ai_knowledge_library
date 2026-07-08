#!/usr/bin/env python3
import urllib.request
import json
import os
from datetime import datetime


def main():
    url = "https://api.first.org/data/v1/epss"
    req = urllib.request.Request(url)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    news_path = os.path.join(repo_root, "documentation", "security_news.md")

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf_8"))
                with open(news_path, "w") as f:
                    f.write("# Latest Security Vulnerability Scores\n\n")
                    f.write(f"Updated: {datetime.now().isoformat()}\n\n")
                    for item in data.get("data", [])[:10]:
                        cve = item.get("cve", "Unknown")
                        epss = item.get("epss", "Unknown")
                        f.write(f"* {cve}: EPSS Score {epss}\n")
                print("Security news updated successfully.")
            else:
                print("Failed to fetch news.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
