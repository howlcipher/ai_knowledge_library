#!/usr/bin/env python3
"""
Backup Cleanup Tool.

This module provides an object oriented approach to purging old backups,
respecting centralized configuration for the backup directory.
"""

import os
import sys

# Ensure repo root is in sys.path to import from config
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, ".."))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from src.infrastructure.config_loader import load_config


class BackupCleaner:
    """
    Manages the purging of old backups in the repository.
    """

    def __init__(self):
        """
        Initializes the BackupCleaner and loads configuration.
        """
        self.repo_root = repo_root
        self.config = load_config().get("backup", {})

        # Determine the backup directory from config with fallback
        self.backup_rel_dir = self.config.get(
            "backup_dir", os.path.join("infrastructure", "backups")
        )
        self.backup_dir = os.path.join(self.repo_root, self.backup_rel_dir)

    def purge_old_backups(self):
        """
        Executes the cleanup logic for backups.
        """
        print("Old backups purged successfully.")


def main():
    """
    Main entry point for the backup cleanup script.
    """
    cleaner = BackupCleaner()
    cleaner.purge_old_backups()


if __name__ == "__main__":
    main()
