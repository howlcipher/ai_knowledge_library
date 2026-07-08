#!/usr/bin/env python3
"""
Web scraping tool for AI research.

This tool fetches content from a given URL, verifies it using an LLM (Gemini),
chunks the text, and inserts it into a vector database (ChromaDB or PGVector).
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from src.infrastructure.config_loader import load_config


class ContentVerifier:
    """Handles the verification of scraped content using an LLM."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ContentVerifier.

        Args:
            api_key (Optional[str]): The Gemini API key. If None, falls back to heuristics.
        """
        cfg = load_config()
        self.api_key = (
            api_key or cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
        )

    def verify(self, text: str, source_url: str) -> Tuple[bool, int, str]:
        """
        Verify the text content for usefulness and factuality.

        Args:
            text (str): The scraped text.
            source_url (str): The URL the text was scraped from.

        Returns:
            Tuple[bool, int, str]: Verification status, confidence score, and reason.
        """
        print("Verifying content integrity...")
        if not self.api_key:
            print(
                "Warning: GEMINI_API_KEY not found. Falling back to basic heuristic checks."
            )
            return self._heuristic_check(text)

        try:
            return self._llm_check(text, source_url)
        except Exception as e:
            print(f"Verification failed: {e}")
            return False, 0, str(e)

    def _heuristic_check(self, text: str) -> Tuple[bool, int, str]:
        """Basic heuristic check when API key is missing."""
        if len(text) < 100:
            return False, 0, "Content too short to verify."
        return True, 70, "Basic check passed (No LLM validation)."

    def _llm_check(self, text: str, source_url: str) -> Tuple[bool, int, str]:
        """LLM-based content verification."""
        import litellm

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

        try:
            fallbacks = [
                "anthropic/claude-3-5-sonnet-20240620",
                "openai/gpt-4o-mini",
            ]
            import time

            start_time = time.time()
            response = litellm.completion(
                model="gemini/gemini-1.5-flash",
                messages=[{"role": "user", "content": prompt}],
                fallbacks=fallbacks,
                api_key=self.api_key,
            )
            latency = time.time() - start_time
            content = response.choices[0].message.content.strip()

            # Log telemetry
            try:
                from src.infrastructure.telemetry_logger import log_telemetry

                cost = litellm.completion_cost(completion_response=response)
                usage = response.usage
                log_telemetry(
                    model=response.model,
                    prompt_tokens=usage.prompt_tokens if usage else 0,
                    completion_tokens=usage.completion_tokens if usage else 0,
                    total_tokens=usage.total_tokens if usage else 0,
                    cost=float(cost) if cost else 0.0,
                    latency=latency,
                )
            except Exception as e:
                import sys

                print(f"Error logging telemetry: {e}", file=sys.stderr)

        except Exception as e:
            print(f"LiteLLM failover exhausted. Error: {e}")
            return False, 0, str(e)

        # Parse JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()

        try:
            result = json.loads(content)
            return (
                result.get("verified", False),
                result.get("confidence", 0),
                result.get("reason", "No reason provided"),
            )
        except Exception as e:
            return False, 0, f"JSON parse error: {e}"


class WebScraper:
    """Handles extracting text content from URLs."""

    def __init__(
        self,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI Knowledge Web Scraper",
    ):
        self.headers = {"User-Agent": user_agent}

    def fetch_text(self, url: str) -> Optional[str]:
        """
        Fetch and extract text from the given URL.

        Args:
            url (str): The URL to scrape.

        Returns:
            Optional[str]: Extracted text or None if fetch fails.
        """
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script, style, and nav elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.extract()

            # Try to find main content, fallback to body
            main_content = (
                soup.find("main") or soup.find("article") or soup.find("body")
            )
            if not main_content:
                main_content = soup

            return main_content.get_text(separator=" ", strip=True)
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return None


class VectorStoreManager:
    """Manages insertion of documents into the configured vector store."""

    def __init__(self, db_mode: str, collection_name: str = "ai_library_knowledge"):
        self.db_mode = db_mode
        self.collection_name = collection_name
        self.batch_size = 100

    def insert(self, docs: List[str], metadatas: List[Dict], ids: List[str]):
        """
        Insert documents into the vector database in batches.
        """
        print(f"Injecting {len(docs)} chunks into {self.db_mode} context...")

        from src.infrastructure.vector_store_factory import VectorStoreFactory

        store = VectorStoreFactory.get_store()
        store.init_db()

        for i in range(0, len(docs), self.batch_size):
            store.upsert(
                docs=docs[i : i + self.batch_size],
                metadatas=metadatas[i : i + self.batch_size],
                ids=ids[i : i + self.batch_size],
            )


class TextChunker:
    """Handles splitting text into manageable, semantically coherent chunks."""

    @staticmethod
    def chunk(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into chunks using LangChain's RecursiveCharacterTextSplitter.
        This provides much better semantic preservation and overlap than naive word counting.
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""],
            )
            return splitter.split_text(text)

        except ImportError:
            print(
                "Warning: langchain-text-splitters not installed. Falling back to naive word chunking."
            )
            # Fallback to naive implementation if not installed
            words = text.split()
            chunks = []
            current_chunk = []
            current_len = 0
            # Naive word counting (approx 5 chars per word roughly maps to max_len)
            max_len = chunk_size // 5

            for word in words:
                if current_len + 1 > max_len:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_len = 1
                else:
                    current_chunk.append(word)
                    current_len += 1

            if current_chunk:
                chunks.append(" ".join(current_chunk))
            return chunks


def main():
    """Main execution point for the web research tool."""
    parser = argparse.ArgumentParser(description="Web scraping tool for AI research.")
    parser.add_argument("--url", type=str, required=True, help="URL to scrape")
    args = parser.parse_args()

    scraper = WebScraper()
    text = scraper.fetch_text(args.url)
    if not text:
        sys.exit(1)

    verifier = ContentVerifier()
    is_verified, trust_score, reason = verifier.verify(text, args.url)

    if not is_verified:
        print(f"Verification Failed: {reason} (Score: {trust_score})")
        print("Aborting ingestion.")
        sys.exit(1)

    print(f"Content Verified (Score: {trust_score}): {reason}")
    print(f"Successfully extracted {len(text)} characters. Chunking...")

    chunks = TextChunker.chunk(text)

    docs_to_insert = []
    metadata_to_insert = []
    ids_to_insert = []

    for i, chunk in enumerate(chunks):
        docs_to_insert.append(chunk)
        metadata_to_insert.append(
            {
                "source": args.url,
                "chunk": i,
                "trust_score": trust_score,
                "verified": True,
            }
        )
        ids_to_insert.append(f"{args.url}_{i}")

    cfg = load_config()
    db_mode = cfg.get("database", {}).get("mode", "sqlite")

    vector_store = VectorStoreManager(db_mode)
    vector_store.insert(docs_to_insert, metadata_to_insert, ids_to_insert)

    print(f"Preview: {text[:200]}...")
    print("Done!")


if __name__ == "__main__":
    main()
