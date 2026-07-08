#!/usr/bin/env python3
"""
Library Backup Tool.

This module provides an object oriented approach to backing up the library.
It utilizes centralized configuration where possible to determine backup targets
and destinations.
"""

import os
import sys
import tarfile

# Ensure repo root is in sys.path to import from config
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, ".."))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from config.loader import load_config


class LibraryBackupManager:
    """
    Manages the creation of library backups.
    """

    def __init__(self):
        """
        Initializes the LibraryBackupManager by loading configuration
        and setting up paths.
        """
        self.repo_root = repo_root
        self.config = load_config().get("backup", {})

        # Read from config with fallbacks
        self.backup_rel_dir = self.config.get(
            "backup_dir", os.path.join("infrastructure", "backups")
        )
        self.backup_dir = os.path.join(self.repo_root, self.backup_rel_dir)
        self.backup_filename = self.config.get("filename", "library_backup.tar.gz")
        self.targets = self.config.get("targets", ["documentation"])

    def create_backup(self):
        """
        Executes the backup process, compressing target directories into a tar archive.
        """
        os.makedirs(self.backup_dir, exist_ok=True)
        out_path = os.path.join(self.backup_dir, self.backup_filename)

        with tarfile.open(out_path, "w:gz") as tar:
            for target in self.targets:
                target_path = os.path.join(self.repo_root, target)
                if os.path.exists(target_path):
                    tar.add(target_path, arcname=target)
                    print(f"Added {target} to backup.")
                else:
                    print(f"Target directory {target_path} does not exist. Skipping.")

        print("Backup completed successfully.")


def main():
    """
    Main entry point for the backup script.
    """
    manager = LibraryBackupManager()
    manager.create_backup()


if __name__ == "__main__":
    main()
