#!/usr/bin/env python3
import yaml
import os


def load_config():
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "settings.yaml"
    )
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


config = load_config()


def main():
    print(f"Loaded config: {config}")


if __name__ == "__main__":
    main()
