#!/usr/bin/env python3
"""
Workspace Bootstrapper

This script initializes a new project workspace by setting up the necessary
directories and anchor files (e.g., WORKSPACE_RULES.md).
"""

import os
import sys


class WorkspaceBootstrapper:
    """Handles the initialization of a project workspace."""

    def __init__(self, project_name: str):
        """
        Initialize the WorkspaceBootstrapper.

        Args:
            project_name (str): The alphanumeric name of the project.
        """
        self.project_name = project_name

    def validate_name(self):
        """Ensure the project name is alphanumeric."""
        if not self.project_name.isalnum():
            print("Error: Name must be alphanumeric")
            sys.exit(1)

    def create_anchor_file(self, base_path: str):
        """Create the WORKSPACE_RULES.md anchor file."""
        anchor_file = os.path.join(base_path, "WORKSPACE_RULES.md")
        content = (
            "name: workspace_anchor\n"
            "description: Triggers on all operations to ground the agent\n\n"
            "# Project Rules\n\n"
            "* Follow all global structural and formatting standards.\n"
        )
        with open(anchor_file, "w") as file_out:
            file_out.write(content)

    def init_workspace(self):
        """Initialize the workspace directories and files."""
        self.validate_name()

        base_path = os.path.join(os.getcwd(), self.project_name, ".agents", "skills")
        os.makedirs(base_path, exist_ok=True)

        self.create_anchor_file(base_path)

        print(f"Workspace telemetry successfully built at: {base_path}")


def main():
    """Main execution point for the script."""
    target = sys.argv[1] if len(sys.argv) > 1 else "new_project"
    bootstrapper = WorkspaceBootstrapper(project_name=target)
    bootstrapper.init_workspace()


if __name__ == "__main__":
    main()
