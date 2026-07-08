#!/usr/bin/env python3
"""
semantic_search.py

Provides an object-oriented interface for performing semantic searches
across the configured vector database backend (PgVector or ChromaDB).
"""

import os
import sys

# Ensure project root is in the path for module loading
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.append(repo_root)

from config.loader import load_config, get_chroma_db_path


class SemanticSearcher:
    """
    Handles semantic search queries by delegating to the appropriate
    vector database backend based on configuration.
    """

    def __init__(self):
        """Initializes the searcher and configures the database connection."""
        self.cfg = load_config()
        self.db_mode = self.cfg.get("database", {}).get("mode", "sqlite")

    def search(self, query: str, n_results: int = 3):
        """
        Executes a semantic search against the database.

        Args:
            query (str): The search string.
            n_results (int): Number of top results to return.
        """
        print(f"Searching for: '{query}' using {self.db_mode} backend...\n")

        if self.db_mode == "pgvector":
            self._search_pgvector(query, n_results)
        else:
            self._search_chromadb(query, n_results)

    def _search_pgvector(self, query: str, n_results: int):
        """Handles searching using PostgreSQL/PgVector."""
        from src.infrastructure.pgvector_backend import PgVectorStore

        store = PgVectorStore()
        results = store.query(query, n_results=n_results)
        if not results:
            print("No relevant results found.")
            return

        for i, row in enumerate(results):
            content, source, distance = row
            text = content[:300] + "..."
            print(f"[{i+1}] Source: {source} (Distance: {distance:.4f})")
            print(f"Snippet: {text}\n")

    def _search_chromadb(self, query: str, n_results: int):
        """Handles searching using the local ChromaDB SQLite backend."""
        try:
            import chromadb
        except ImportError:
            print("Error: chromadb not installed.")
            sys.exit(1)

        db_path = get_chroma_db_path()
        if not os.path.exists(db_path):
            print(
                "Vector database not found. Please run src/infrastructure/build_vector_index.py first."
            )
            sys.exit(1)

        client = chromadb.PersistentClient(path=db_path)
        try:
            collection = client.get_collection(name="ai_library_knowledge")
        except Exception:
            print("Collection not found. Please rebuild the index.")
            sys.exit(1)

        results = collection.query(query_texts=[query], n_results=n_results)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            print("No relevant results found.")
            return

        for i in range(len(documents)):
            source = metadatas[i].get("source", "Unknown") if metadatas else "Unknown"
            dist = distances[i] if distances else 0.0
            text = documents[i][:300] + "..."
            print(f"[{i+1}] Source: {source} (Distance: {dist:.4f})")
            print(f"Snippet: {text}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: semantic_search.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    searcher = SemanticSearcher()
    searcher.search(query)


if __name__ == "__main__":
    main()
