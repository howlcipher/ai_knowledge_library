#!/usr/bin/env python3
"""
Log Cleanup Tool.

This module provides an object oriented approach to removing outdated log files.
It reads retention policies and log directories from the centralized configuration.
"""

import os
import sys
import time

# Ensure repo root is in sys.path to import from config
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, ".."))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from src.infrastructure.config_loader import load_config


class LogCleaner:
    """
    Manages the cleanup of old log files based on retention policies.
    """

    def __init__(self):
        """
        Initializes the LogCleaner and loads configuration.
        """
        self.repo_root = repo_root
        self.config = load_config().get("logs", {})

        # Load directory and retention configuration with fallbacks
        self.log_rel_dir = self.config.get(
            "log_dir", os.path.join("infrastructure", "logs")
        )
        self.log_dir = os.path.join(self.repo_root, self.log_rel_dir)
        self.retention_days = self.config.get("retention_days", 7)
        self.retention_seconds = self.retention_days * 24 * 60 * 60

    def clean_logs(self):
        """
        Iterates over the log directory and removes files older than the retention period.
        """
        if not os.path.exists(self.log_dir):
            print("Log directory does not exist.")
            return

        current_time = time.time()

        for filename in os.listdir(self.log_dir):
            filepath = os.path.join(self.log_dir, filename)
            if os.path.isfile(filepath):
                file_mod_time = os.path.getmtime(filepath)
                if current_time > file_mod_time + self.retention_seconds:
                    os.remove(filepath)
                    print(f"Removed old log: {filename}")

        print("Log cleanup complete.")


def main():
    """
    Main entry point for the log cleanup script.
    """
    cleaner = LogCleaner()
    cleaner.clean_logs()


if __name__ == "__main__":
    main()
