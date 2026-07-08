#!/usr/bin/env python3
"""
Cron Job Setup Script

This script configures the system crontab to include scheduled jobs
for the AI Knowledge Library, such as fetching news and cleaning logs.
"""

import os
import subprocess
from typing import List


class CronManager:
    """Manages the configuration and updating of system cron jobs."""

    def __init__(self, repo_root: str):
        """
        Initialize the CronManager.

        Args:
            repo_root (str): The root directory of the repository.
        """
        self.repo_root = repo_root

    def get_jobs(self) -> List[str]:
        """Define the cron jobs to be installed."""
        fetch_news = os.path.join(self.repo_root, "scripts", "fetch_security_news.py")
        clean_logs = os.path.join(self.repo_root, "scripts", "clean_logs.py")

        return [
            f"0 8 * * * python3 {fetch_news}\n",
            f"0 0 * * * python3 {clean_logs}\n",
        ]

    def _get_current_crontab(self) -> str:
        """Retrieve the current crontab for the user."""
        import shutil

        crontab_exe = shutil.which("crontab")
        if not crontab_exe:
            return ""
        try:
            flag = chr(45) + "l"
            return subprocess.check_output([crontab_exe, flag]).decode("utf8")
        except subprocess.CalledProcessError:
            return ""

    def _apply_crontab(self, cron_content: str):
        """Apply new cron content to the system."""
        import shutil
        import tempfile

        crontab_exe = shutil.which("crontab")
        if not crontab_exe:
            print("Failed to apply crontab: crontab not found in PATH.")
            return

        fd, cron_file = tempfile.mkstemp()
        with os.fdopen(fd, "w") as f:
            f.write(cron_content)
        subprocess.run([crontab_exe, cron_file])
        os.remove(cron_file)

    def update_crontab(self):
        """Update the system crontab with defined jobs if missing."""
        current_cron = self._get_current_crontab()
        jobs = self.get_jobs()

        new_cron = current_cron
        for job in jobs:
            if job.strip() not in current_cron:
                new_cron += job

        if new_cron != current_cron:
            self._apply_crontab(new_cron)
            print("System crontab updated successfully.")
        else:
            print("System crontab already properly configured.")


def main():
    """Main execution point for the cron setup script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    manager = CronManager(repo_root)
    manager.update_crontab()


if __name__ == "__main__":
    main()
