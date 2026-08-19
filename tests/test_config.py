import os
import sys
import pytest
from pydantic import ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.infrastructure.config_loader import (
    load_config,
    get_chroma_db_path,
    is_local_only,
    is_connected,
    AppSettings,
    ConfigLoader,
)


def test_load_config():
    config = load_config()
    assert isinstance(config, dict)
    assert "database" in config
    assert "mode" in config["database"]
    assert "operating_mode" in config
    assert config["operating_mode"] in ("local_only", "connected")


def test_get_chroma_db_path():
    path = get_chroma_db_path()
    assert os.path.isabs(path)
    assert "chroma" in path.lower()


def test_operating_mode_defaults_and_helpers():
    settings = AppSettings()
    assert settings.operating_mode == "local_only"

    # Default loader
    loader = ConfigLoader()
    assert loader.is_local_only() is True
    assert loader.is_connected() is False
    assert is_local_only() is True
    assert is_connected() is False


def test_operating_mode_connected():
    settings = AppSettings(operating_mode="connected")
    assert settings.operating_mode == "connected"


def test_operating_mode_invalid_raises():
    with pytest.raises(ValidationError):
        AppSettings(operating_mode="unrestricted_cloud")

