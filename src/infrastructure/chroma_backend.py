import os
import sys
from typing import Dict, List, Optional, Tuple

from src.infrastructure.config_loader import get_chroma_db_path
from src.infrastructure.vector_store_base import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str = "ai_library_knowledge"):
        try:
            import chromadb
        except ImportError:
            print("Error: chromadb not installed.")
            sys.exit(1)

        self.collection_name = collection_name
        self.db_path = get_chroma_db_path()
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.db_path)

    def init_db(self) -> None:
        """ChromaDB initializes implicitly."""

    def reset(self) -> None:
        """Drop the collection so a rebuild starts empty; upsert recreates it."""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            # Collection does not exist yet; nothing to drop.
            pass

    def upsert(
        self, docs: List[str], metadatas: List[Dict], ids: Optional[List[str]] = None
    ) -> None:
        collection = self.client.get_or_create_collection(name=self.collection_name)

        if not ids:
            ids = [f"doc_{i}" for i in range(len(docs))]

        collection.upsert(
            documents=docs,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, text: str, n_results: int = 5) -> List[Tuple[str, str, float]]:
        try:
            collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            print("Collection not found. Please rebuild the index.")
            return []

        results = collection.query(query_texts=[text], n_results=n_results)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        out = []
        for i in range(len(documents)):
            source = metadatas[i].get("source", "Unknown") if metadatas else "Unknown"
            dist = distances[i] if distances else 0.0
            doc = documents[i]
            out.append((doc, source, dist))
        return out
