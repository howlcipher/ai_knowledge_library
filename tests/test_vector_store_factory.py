import os
import sys
import pytest
from unittest.mock import patch

# Ensure project root is on sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.infrastructure.config_loader import ConfigLoader, default_loader
from src.infrastructure.vector_store_factory import VectorStoreFactory


def test_configloader_custom_indexing(tmp_path):
    """ConfigLoader should round‑trip a custom indexing collection_name from YAML."""
    yaml_content = """
indexing:
  collection_name: custom_collection_name
"""
    config_file = tmp_path / "settings.yaml"
    config_file.write_text(yaml_content)
    loader = ConfigLoader(str(config_file))
    assert loader.get("indexing")["collection_name"] == "custom_collection_name"


def test_configloader_default_indexing():
    """ConfigLoader should provide default indexing values when block is missing."""
    indexing = default_loader.get("indexing")
    assert indexing["collection_name"] == "ai_library_knowledge"
    assert indexing["max_chunk_length"] == 1000
    assert indexing["batch_size"] == 100


def test_vectorstorefactory_chroma_collection_name(monkeypatch):
    """VectorStoreFactory should pass the configured collection_name to ChromaVectorStore."""
    def fake_get(key, default=None):
        if key == "indexing":
            return {"collection_name": "custom_test_collection"}
        if key == "database":
            return {"mode": "sqlite"}
        return default
    monkeypatch.setattr(default_loader, "get", fake_get)

    class DummyChroma:
        def __init__(self, collection_name: str = "ai_library_knowledge"):
            self.collection_name = collection_name
        def init_db(self):
            pass
        def reset(self):
            pass
        def upsert(self, docs, metadatas, ids=None):
            pass

    import src.infrastructure.chroma_backend as chroma_mod
    monkeypatch.setattr(chroma_mod, "ChromaVectorStore", DummyChroma)

    store = VectorStoreFactory.get_store()
    assert isinstance(store, DummyChroma)
    assert store.collection_name == "custom_test_collection"


def test_vectorstorefactory_pgvector_branch(monkeypatch):
    """VectorStoreFactory should return PgVectorStore when mode is pgvector and not pass collection_name."""
    def fake_get(key, default=None):
        if key == "database":
            return {"mode": "pgvector"}
        return default
    monkeypatch.setattr(default_loader, "get", fake_get)

    init_args = {}
    class DummyPgVector:
        def __init__(self, *args, **kwargs):
            init_args["args"] = args
            init_args["kwargs"] = kwargs
        def init_db(self):
            pass
        def reset(self):
            pass
        def upsert(self, docs, metadatas, ids=None):
            pass

    import src.infrastructure.pgvector_backend as pg_mod
    monkeypatch.setattr(pg_mod, "PgVectorStore", DummyPgVector)

    store = VectorStoreFactory.get_store()
    assert isinstance(store, DummyPgVector)
    assert init_args["args"] == ()
    assert init_args["kwargs"] == {}
