#!/usr/bin/env python3
import yaml
import os


from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    chroma_db_path: str = ".chroma"
    pgvector_dsn: str = ""
    mode: str = "sqlite"

class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    webhook_secret: str = ""

class AgentsSettings(BaseModel):
    default_language: str = "en_US"
    max_context_tokens: int = 8192

class BackupSettings(BaseModel):
    targets: list = ["documentation"]
    backup_dir: str = "infrastructure/backups"
    filename: str = "library_backup.tar.gz"

class AppSettings(BaseSettings):
    llm_model: str = "gemini/gemini-1.5-pro"
    gemini_api_key: str = ""
    database: DatabaseSettings = DatabaseSettings()
    server: ServerSettings = ServerSettings()
    agents: AgentsSettings = AgentsSettings()
    backup: BackupSettings = BackupSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            env_settings,
            dotenv_settings,
            init_settings,
            file_secret_settings,
        )

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
        self.repo_root = os.path.dirname(os.path.dirname(self.script_dir))

        if config_path is None:
            self.config_path = os.path.join(self.repo_root, "config", "settings.yaml")
        else:
            self.config_path = config_path

        yaml_data = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                yaml_data = yaml.safe_load(f) or {}

        # Load pydantic settings prioritizing .env over yaml_data
        self.settings = AppSettings(**yaml_data)
        self.config = self.settings.model_dump()

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
    return default_loader.config


def main():
    """
    Main entry point for testing the ConfigLoader.
    """
    print(f"Loaded config: {config}")


if __name__ == "__main__":
    main()

def get_chroma_db_path():
    """
    Returns the absolute path to the ChromaDB directory.
    """
    db_path = default_loader.get("database", {}).get("chroma_db_path", ".chromadb")
    return os.path.abspath(os.path.join(default_loader.get_repo_root(), db_path))
