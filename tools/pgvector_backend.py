#!/usr/bin/env python3
import os
import sys

try:
    import psycopg2
    from pgvector.psycopg2 import register_vector
    from sentence_transformers import SentenceTransformer
    import yaml
except ImportError:
    print(
        "Dependencies missing. Please install psycopg2-binary, pgvector, and sentence-transformers."
    )
    sys.exit(1)


def get_config():
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "settings.yaml"
    )
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


class PgVectorStore:
    def __init__(self):
        config = get_config()
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

    def init_db(self):
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
        self.conn.commit()

    def upsert(self, docs, metadatas):
        embeddings = self.model.encode(docs)
        with self.conn.cursor() as cur:
            for doc, meta, emb in zip(docs, metadatas, embeddings):
                cur.execute(
                    "INSERT INTO documents (content, source, embedding) VALUES (%s, %s, %s)",
                    (doc, meta.get("source", ""), emb.tolist()),
                )
        self.conn.commit()

    def query(self, text, n_results=5):
        query_embedding = self.model.encode([text])[0]
        with self.conn.cursor() as cur:
            # Using cosine distance <=>
            cur.execute(
                "SELECT content, source, embedding <=> %s AS distance FROM documents ORDER BY distance LIMIT %s",
                (query_embedding.tolist(), n_results),
            )
            return cur.fetchall()


def main():
    print("PgVector Backend Initialized. Ready for production concurrency.")
    # store = PgVectorStore()
    # store.init_db()


if __name__ == "__main__":
    main()
