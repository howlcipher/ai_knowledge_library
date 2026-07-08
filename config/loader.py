import os
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

def get_chroma_db_path():
    db_path = config.get("database", {}).get("chroma_db_path", ".chromadb")
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), db_path))
