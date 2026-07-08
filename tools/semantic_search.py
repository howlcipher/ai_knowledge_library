#!/usr/bin/env python3
import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: semantic_search.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    sys.path.append(repo_root)

    from config.loader import load_config, get_chroma_db_path

    cfg = load_config()
    db_mode = cfg.get("database", {}).get("mode", "sqlite")

    print(f"Searching for: '{query}' using {db_mode} backend...\n")

    if db_mode == "pgvector":
        from tools.pgvector_backend import PgVectorStore

        store = PgVectorStore()
        results = store.query(query, n_results=3)
        if not results:
            print("No relevant results found.")
            return
        for i, row in enumerate(results):
            content, source, distance = row
            text = content[:300] + "..."
            print(f"[{i+1}] Source: {source} (Distance: {distance:.4f})")
            print(f"Snippet: {text}\n")
    else:
        try:
            import chromadb
        except ImportError:
            print("Error: chromadb not installed.")
            sys.exit(1)

        db_path = get_chroma_db_path()
        if not os.path.exists(db_path):
            print(
                "Vector database not found. Please run tools/build_vector_index.py first."
            )
            sys.exit(1)

        client = chromadb.PersistentClient(path=db_path)
        try:
            collection = client.get_collection(name="ai_library_knowledge")
        except Exception:
            print("Collection not found. Please rebuild the index.")
            sys.exit(1)

        results = collection.query(query_texts=[query], n_results=3)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        if not documents:
            print("No relevant results found.")
            return

        for i in range(len(documents)):
            source = metadatas[i]["source"]
            dist = distances[i]
            text = documents[i][:300] + "..."
            print(f"[{i+1}] Source: {source} (Distance: {dist:.4f})")
            print(f"Snippet: {text}\n")


if __name__ == "__main__":
    main()
