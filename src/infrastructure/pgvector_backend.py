#!/usr/bin/env python3
"""
Module for interacting with a PostgreSQL database using the pgvector extension.
"""

import sys

try:
    import psycopg2
    from pgvector.psycopg2 import register_vector
    from sentence_transformers import SentenceTransformer
except ImportError:
    print(
        "Dependencies missing. Please install psycopg2-binary, pgvector, and sentence-transformers."
    )
    sys.exit(1)


from src.infrastructure.config_loader import load_config
from src.infrastructure.vector_store_base import BaseVectorStore


class PgVectorStore(BaseVectorStore):
    """
    Handles operations for the PostgreSQL vector database.
    """

    def __init__(self):
        """
        Initializes the PgVectorStore, establishing a database connection
        and loading the sentence transformer model.
        """
        config = load_config()
        dsn = config.get("database", {}).get(
            "pgvector_dsn", "postgresql://localhost:5432/ai_knowledge"
        )

        try:
            self.conn = psycopg2.connect(dsn)
            register_vector(self.conn)
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            sys.exit(1)

    def init_db(self) -> None:
        """
        Initializes the database by creating the necessary extension and table,
        and adds an HNSW index for high-performance approximate nearest neighbor search.
        """
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    source TEXT,
                    embedding vector(384)
                )
            """)
            # Create HNSW index for optimal search performance using cosine distance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS documents_embedding_hnsw_idx 
                ON documents USING hnsw (embedding vector_cosine_ops)
            """)
        self.conn.commit()

    def reset(self) -> None:
        """
        Empty the documents table so a rebuild starts clean. Required for
        idempotency: upsert() below is a plain INSERT, so rerunning a build
        without a reset duplicates every row.
        """
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE documents RESTART IDENTITY")
        self.conn.commit()

    def upsert(self, docs: list, metadatas: list, ids: list = None) -> None:
        """
        Encodes documents into embeddings and inserts them into the database.

        Args:
            docs (list): A list of document strings.
            metadatas (list): A list of metadata dictionaries corresponding to the documents.
            ids (list, optional): A list of document IDs.
        """
        embeddings = self.model.encode(docs)
        with self.conn.cursor() as cur:
            for doc, meta, emb in zip(docs, metadatas, embeddings):
                cur.execute(
                    "INSERT INTO documents (content, source, embedding) VALUES (%s, %s, %s)",
                    (doc, meta.get("source", ""), emb.tolist()),
                )
        self.conn.commit()

    def query(self, text: str, n_results: int = 5) -> list:
        """
        Queries the database for documents similar to the provided text.

        Args:
            text (str): The search query text.
            n_results (int, optional): The number of results to return. Defaults to 5.

        Returns:
            list: A list of tuples containing the matched documents and their sources.
        """
        query_embedding = self.model.encode([text])[0]
        with self.conn.cursor() as cur:
            # Using cosine distance <=>
            cur.execute(
                "SELECT content, source, embedding <=> %s AS distance FROM documents ORDER BY distance LIMIT %s",
                (query_embedding.tolist(), n_results),
            )
            return cur.fetchall()


def main():
    """
    Main entry point for the script.
    """
    print("PgVector Backend Initialized. Ready for production concurrency.")
    # store = PgVectorStore()
    # store.init_db()


if __name__ == "__main__":
    main()
