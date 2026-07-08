#!/usr/bin/env python3
import os
import urllib.request
import json
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_loader import ConfigLoader


class AgentSummaryGenerator:
    """
    Class responsible for generating the agent summary dynamically.
    """

    def __init__(self):
        """
        Initializes the generator with configuration settings.
        """
        self.config_loader = ConfigLoader()
        self.username = self.config_loader.get("github_username", "howlcipher")
        self.api_url = self.config_loader.get(
            "github_api_base_url", "https://api.github.com/users/"
        )

        default_path = os.path.join(
            self.config_loader.get_repo_root(), ".agents", "rules", "user_summary.md"
        )
        self.summary_path = self.config_loader.get("agent_summary_path", default_path)

    def fetch_github_data(self):
        """
        Fetches GitHub repository count and bio for the configured user.
        """
        url = f"{self.api_url}{self.username}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf_8"))
                    return data.get("public_repos", 0), data.get("bio", "")
        except Exception:
            pass
        return None, None

    def generate_summary(self):
        """
        Generates the summary markdown file with user profile and live data.
        """
        repos, bio = self.fetch_github_data()

        dash = chr(45)
        yaml_border = dash * 3 + "\n"

        summary = [
            yaml_border,
            "name: user_summary\n",
            "description: Condensed user profile for quick context injection.\n",
            yaml_border,
            "User is William Elias, a Software Engineer specializing in Cyber Defense.\n",
            "Core capabilities include Python, Go, Docker, and secure Cloud architecture.\n",
        ]

        if repos is not None:
            summary.append(f"Live GitHub Stats: {repos} public repositories.\n")
        if bio:
            summary.append(f"Live GitHub Bio: {bio}\n")

        os.makedirs(os.path.dirname(self.summary_path), exist_ok=True)
        with open(self.summary_path, "w") as f:
            f.writelines(summary)

        print(
            "Agent summary generated with dynamic API data at .agents/rules/user_summary.md"
        )


def main():
    """
    Main function to execute the summary generator.
    """
    generator = AgentSummaryGenerator()
    generator.generate_summary()


if __name__ == "__main__":
    main()
