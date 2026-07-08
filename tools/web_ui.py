#!/usr/bin/env python3
import os
import sys

try:
    import streamlit as st
    import chromadb
except ImportError:
    print("Error: streamlit or chromadb not installed. Run 'pip install streamlit chromadb sentence-transformers'")
    sys.exit(1)

def get_chroma_client():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    db_path = os.path.join(repo_root, ".chromadb")
    
    if not os.path.exists(db_path):
        st.error("Vector database not found. Please run tools/build_vector_index.py first.")
        st.stop()
        
    return chromadb.PersistentClient(path=db_path)

def main():
    st.set_page_config(page_title="AI Knowledge Library Chat", layout="wide")
    
    st.title("🤖 AI Knowledge Library - RAG Chat")
    st.markdown("Search and chat with the repository context directly from your browser!")
    
    client = get_chroma_client()
    try:
        collection = client.get_collection(name="ai_library_knowledge")
    except Exception:
        st.error("Collection not found. Please rebuild the index.")
        st.stop()
        
    query = st.text_input("Enter your query to search the knowledge base:")
    
    if st.button("Search") and query:
        with st.spinner("Searching..."):
            results = collection.query(
                query_texts=[query],
                n_results=5
            )
            
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            if not documents:
                st.warning("No relevant results found.")
            else:
                st.success("Found relevant context!")
                for i in range(len(documents)):
                    source = metadatas[i]['source']
                    dist = distances[i]
                    text = documents[i]
                    
                    with st.expander(f"Result {i+1} | Source: {source} (Confidence: {1 - dist:.2f})"):
                        st.write(text)

if __name__ == "__main__":
    main()
