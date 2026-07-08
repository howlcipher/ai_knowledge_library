#!/usr/bin/env python3
import yaml
import os


class ConfigLoader:
    """
    A class to load and provide access to configuration settings,
    as well as common directory paths to apply DRY principles.
    """

    def __init__(self, config_path=None):
        """
        Initializes the ConfigLoader and calculates common paths.
        """
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.repo_root = os.path.dirname(self.script_dir)

        if config_path is None:
            self.config_path = os.path.join(self.repo_root, "config", "settings.yaml")
        else:
            self.config_path = config_path

        self.config = self._load_config()

    def _load_config(self):
        """
        Loads the configuration from the specified YAML file.
        Returns an empty dictionary if the file does not exist.
        """
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f) or {}

    def get(self, key, default=None):
        """
        Retrieves a value from the configuration using the provided key.
        """
        return self.config.get(key, default)

    def get_repo_root(self):
        """
        Returns the root directory of the repository.
        """
        return self.repo_root


# Provide a default instance and config dictionary for backward compatibility
default_loader = ConfigLoader()
config = default_loader.config


def load_config():
    """
    Legacy function to load config directly.
    """
    return default_loader._load_config()


def main():
    """
    Main entry point for testing the ConfigLoader.
    """
    print(f"Loaded config: {config}")


if __name__ == "__main__":
    main()
