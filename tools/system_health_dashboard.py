#!/usr/bin/env python3
"""
System Health Dashboard Generator.
"""

import os


class DashboardGenerator:
    """Class to generate a system health dashboard HTML file."""

    def __init__(self, out_path: str = None):
        """Initializes the generator."""
        if out_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            repo_root = os.path.dirname(script_dir)
            self.out_path = os.path.join(repo_root, "infrastructure", "dashboard.html")
        else:
            self.out_path = out_path

    def generate(self) -> None:
        """Generates the HTML dashboard."""
        html_content = "<html><body><h1>System Health</h1><p>All systems operational.</p></body></html>\n"
        with open(self.out_path, "w") as f:
            f.write(html_content)

        print("Dashboard generated.")


def main():
    """Main entry point."""
    generator = DashboardGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
