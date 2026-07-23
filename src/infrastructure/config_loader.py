#!/usr/bin/env python3
import os

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.infrastructure.secret_manager import SecretManager


class DatabaseSettings(BaseModel):
    chroma_db_path: str = ".chroma"
    pgvector_dsn: str = ""
    mode: str = "sqlite"


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"  # nosec B104
    port: int = 8000
    webhook_secret: str = ""


class AgentsSettings(BaseModel):
    default_language: str = "en_US"
    max_context_tokens: int = 8192


class BackupSettings(BaseModel):
    targets: list = ["documentation"]
    backup_dir: str = "infrastructure/backups"
    filename: str = "library_backup.tar.gz"


class TierModelsSettings(BaseModel):
    tier_1: str = ""
    tier_2: str = ""
    tier_3: str = ""


class TierTimeoutsSettings(BaseModel):
    tier_1: float = 0.0
    tier_2: float = 0.0
    tier_3: float = 0.0


class PayloadPipelineSettings(BaseModel):
    enabled: bool = False
    max_attempts: int = 3
    artifact_dir: str = "logs/payloads"
    preflight: bool = True
    preflight_timeout: float = 120.0
    timeout: float = 600.0
    transport_retries: int = 2
    transport_backoff: float = 2.0
    structured_outputs: bool = True
    tier_models: TierModelsSettings = TierModelsSettings()
    tier_timeouts: TierTimeoutsSettings = TierTimeoutsSettings()


class SkillRouterSettings(BaseModel):
    enabled: bool = True
    top_k: int = 3
    score_threshold: float = 0.0
    max_context_chars: int = 12000
    skills_dir: str = ".agents/skills"


class IndexingSettings(BaseModel):
    collection_name: str = "ai_library_knowledge"
    max_chunk_length: int = 1000
    batch_size: int = 100


class AppSettings(BaseSettings):
    llm_model: str = "gemini/gemini-1.5-pro"
    llm_timeout: float = 600.0
    preflight: bool = True
    mcp_connect_timeout: float = 30.0
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    database: DatabaseSettings = DatabaseSettings()
    server: ServerSettings = ServerSettings()
    agents: AgentsSettings = AgentsSettings()
    backup: BackupSettings = BackupSettings()
    skill_router: SkillRouterSettings = SkillRouterSettings()
    indexing: IndexingSettings = IndexingSettings()
    payload_pipeline: PayloadPipelineSettings = PayloadPipelineSettings()
    active_mcps: list = []
    mcp_servers: dict = {}

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", extra="ignore"
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

        # Override with Secret Manager if configured
        secret_mgr = SecretManager()
        if os.environ.get("USE_AWS_SECRETS_MANAGER") == "true":
            aws_api_key = secret_mgr.get_secret("GEMINI_API_KEY")
            if aws_api_key:
                self.settings.gemini_api_key = aws_api_key

            aws_anthropic_key = secret_mgr.get_secret("ANTHROPIC_API_KEY")
            if aws_anthropic_key:
                self.settings.anthropic_api_key = aws_anthropic_key

            aws_webhook = secret_mgr.get_secret("WEBHOOK_SECRET")
            if aws_webhook:
                self.settings.server.webhook_secret = aws_webhook

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


def resolve_utility_llm(cfg=None):
    """
    Picks a fast, cheap LiteLLM model for internal utility calls (query
    expansion, content verification) based on whichever provider API key
    is configured. Returns a (model, api_key) tuple, or (None, None) if
    no provider key is available.
    """
    cfg = cfg or default_loader.config
    gemini_key = cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        return "gemini/gemini-1.5-flash", gemini_key

    anthropic_key = cfg.get("anthropic_api_key") or os.environ.get(
        "ANTHROPIC_API_KEY"
    )
    if anthropic_key:
        return "anthropic/claude-haiku-4-5-20251001", anthropic_key

    return None, None
