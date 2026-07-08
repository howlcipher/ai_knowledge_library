#!/usr/bin/env python3
import os
import sys
import glob

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    pass # Might not be needed if using pgvector

def chunk_text(text, max_len=1000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0
    for word in words:
        if current_len + len(word) > max_len:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_len = len(word)
        else:
            current_chunk.append(word)
            current_len += len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    sys.path.append(repo_root)  # Ensure root is in path for imports
    
    from config.loader import load_config, get_chroma_db_path
    
    cfg = load_config()
    db_mode = cfg.get("database", {}).get("mode", "sqlite")
    
    docs_to_insert = []
    metadata_to_insert = []
    ids_to_insert = []
    
    print("Scanning for markdown files...")
    md_files = glob.glob(os.path.join(repo_root, "**", "*.md"), recursive=True)
    
    for file_path in md_files:
        if ".git" in file_path or (".agents" not in file_path and "documentation" not in file_path and "README" not in file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip(): continue
                
                rel_path = os.path.relpath(file_path, repo_root)
                chunks = chunk_text(content)
                
                for i, chunk in enumerate(chunks):
                    docs_to_insert.append(chunk)
                    metadata_to_insert.append({"source": rel_path, "chunk": i})
                    ids_to_insert.append(f"{rel_path}_{i}")
                    
        except Exception as e:
            print(f"Skipping {file_path}: {e}")

    if not docs_to_insert:
        print("No markdown content found to index.")
        return

    print(f"Inserting {len(docs_to_insert)} chunks into {db_mode} database...")
    batch_size = 100

    if db_mode == "pgvector":
        from tools.pgvector_backend import PgVectorStore
        store = PgVectorStore()
        store.init_db()
        for i in range(0, len(docs_to_insert), batch_size):
            store.upsert(
                docs=docs_to_insert[i:i+batch_size],
                metadatas=metadata_to_insert[i:i+batch_size]
            )
    else:
        db_path = get_chroma_db_path()
        print(f"Initializing ChromaDB at {db_path}...")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(name="ai_library_knowledge")
        for i in range(0, len(docs_to_insert), batch_size):
            collection.upsert(
                documents=docs_to_insert[i:i+batch_size],
                metadatas=metadata_to_insert[i:i+batch_size],
                ids=ids_to_insert[i:i+batch_size]
            )
            
    print("Knowledge base indexing complete!")

if __name__ == "__main__":
    main()
