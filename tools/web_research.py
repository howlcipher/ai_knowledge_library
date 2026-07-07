#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import argparse

def extract_text_from_url(url):
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return text[:5000] # Limit to first 5000 chars for demo
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Web scraping tool for AI research.")
    parser.add_argument("--url", type=str, required=True, help="URL to scrape")
    args = parser.parse_args()
    
    text = extract_text_from_url(args.url)
    if text:
        print("Successfully extracted content. Injecting into ChromaDB context...")
        # In a real environment, this gets chunked and embedded via chromadb
        print(f"Preview: {text[:200]}...")

if __name__ == "__main__":
    main()
