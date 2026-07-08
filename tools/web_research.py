#!/usr/bin/env python3
import sys
import os
import argparse
import requests
import json
from bs4 import BeautifulSoup

# Ensure root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.append(repo_root)

from config.loader import load_config, get_chroma_db_path

def verify_content(text, source_url):
    print("Verifying content integrity...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Falling back to basic heuristic checks.")
        # Basic heuristic check
        if len(text) < 100:
            return False, 0, "Content too short to verify."
        return True, 70, "Basic check passed (No LLM validation)."
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an AI data verifier for a knowledge graph.
        Analyze the following scraped text from {source_url}.
        Determine if the text contains useful, factual information or if it is spam, hallucinated, or irrelevant filler.
        Return a JSON object with three keys:
        - "verified": true/false
        - "confidence": integer 0-100
        - "reason": brief explanation
        
        Text snippet (first 3000 chars):
        {text[:3000]}
        """
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        # Parse JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        result = json.loads(content)
        return result.get("verified", False), result.get("confidence", 0), result.get("reason", "No reason provided")
    except Exception as e:
        print(f"Verification failed: {e}")
        return False, 0, str(e)

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

def extract_text_from_url(url):
    try:
        print(f"Fetching {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI Knowledge Web Scraper'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, and nav elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.extract()
            
        # Try to find main content, fallback to body
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if not main_content:
            main_content = soup
            
        text = main_content.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Web scraping tool for AI research.")
    parser.add_argument("--url", type=str, required=True, help="URL to scrape")
    args = parser.parse_args()
    
    text = extract_text_from_url(args.url)
    if not text:
        sys.exit(1)
        
    is_verified, trust_score, reason = verify_content(text, args.url)
    if not is_verified:
        print(f"Verification Failed: {reason} (Score: {trust_score})")
        print("Aborting ingestion.")
        sys.exit(1)
        
    print(f"Content Verified (Score: {trust_score}): {reason}")
    print(f"Successfully extracted {len(text)} characters. Chunking...")
    chunks = chunk_text(text)
    
    docs_to_insert = []
    metadata_to_insert = []
    ids_to_insert = []
    
    for i, chunk in enumerate(chunks):
        docs_to_insert.append(chunk)
        metadata_to_insert.append({
            "source": args.url, 
            "chunk": i,
            "trust_score": trust_score,
            "verified": True
        })
        ids_to_insert.append(f"{args.url}_{i}")
        
    cfg = load_config()
    db_mode = cfg.get("database", {}).get("mode", "sqlite")
    
    print(f"Injecting {len(chunks)} chunks into {db_mode} context...")
    
    batch_size = 100
    if db_mode == "pgvector":
        from tools.pgvector_backend import PgVectorStore
        store = PgVectorStore()
        for i in range(0, len(docs_to_insert), batch_size):
            store.upsert(
                docs=docs_to_insert[i:i+batch_size],
                metadatas=metadata_to_insert[i:i+batch_size]
            )
    else:
        try:
            import chromadb
        except ImportError:
            print("Error: chromadb not installed.")
            sys.exit(1)
            
        db_path = get_chroma_db_path()
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(name="ai_library_knowledge")
        for i in range(0, len(docs_to_insert), batch_size):
            collection.upsert(
                documents=docs_to_insert[i:i+batch_size],
                metadatas=metadata_to_insert[i:i+batch_size],
                ids=ids_to_insert[i:i+batch_size]
            )
            
    print(f"Preview: {text[:200]}...")
    print("Done!")

if __name__ == "__main__":
    main()
