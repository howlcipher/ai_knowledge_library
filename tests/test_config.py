import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.loader import load_config, get_chroma_db_path

def test_load_config():
    config = load_config()
    assert isinstance(config, dict)
    assert "database" in config
    assert "mode" in config["database"]

def test_get_chroma_db_path():
    path = get_chroma_db_path()
    assert os.path.isabs(path)
    assert "chroma" in path.lower()
