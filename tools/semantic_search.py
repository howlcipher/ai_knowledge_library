#!/usr/bin/env python3
import os
import sys

try:
    import chromadb
except ImportError:
    print("Error: chromadb not installed. Run 'pip install chromadb sentence-transformers'")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: semantic_search.py <query>")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    db_path = os.path.join(repo_root, ".chromadb")
    
    if not os.path.exists(db_path):
        print("Vector database not found. Please run tools/build_vector_index.py first.")
        sys.exit(1)
        
    client = chromadb.PersistentClient(path=db_path)
    try:
        collection = client.get_collection(name="ai_library_knowledge")
    except Exception:
        print("Collection not found. Please rebuild the index.")
        sys.exit(1)
        
    print(f"Searching for: '{query}'...\n")
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    if not documents:
        print("No relevant results found.")
        return
        
    for i in range(len(documents)):
        source = metadatas[i]['source']
        dist = distances[i]
        text = documents[i][:300] + "..."
        print(f"[{i+1}] Source: {source} (Distance: {dist:.4f})")
        print(f"Snippet: {text}\n")
        
if __name__ == "__main__":
    main()
