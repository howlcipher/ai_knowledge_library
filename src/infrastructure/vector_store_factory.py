from src.infrastructure.config_loader import default_loader
from src.infrastructure.vector_store_base import BaseVectorStore


class VectorStoreFactory:
    """Factory to retrieve the configured Vector Store backend."""

    @staticmethod
    def get_store() -> BaseVectorStore:
        db_mode = default_loader.get("database", {}).get("mode", "sqlite")

        if db_mode == "pgvector":
            from src.infrastructure.pgvector_backend import PgVectorStore

            return PgVectorStore()
        else:
            from src.infrastructure.chroma_backend import ChromaVectorStore

            return ChromaVectorStore()
