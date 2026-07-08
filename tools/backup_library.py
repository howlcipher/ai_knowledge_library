#!/usr/bin/env python3
import os
import tarfile


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    backup_dir = os.path.join(repo_root, "infrastructure", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    out_path = os.path.join(backup_dir, "library_backup.tar.gz")
    with tarfile.open(out_path, "w:gz") as tar:
        tar.add(os.path.join(repo_root, "documentation"), arcname="documentation")
    print("Backup completed successfully.")


if __name__ == "__main__":
    main()
