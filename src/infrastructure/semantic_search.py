#!/usr/bin/env python3
"""
semantic_search.py

Provides an object-oriented interface for performing semantic searches
across the configured vector database backend (PgVector or ChromaDB).
"""

import sys

from src.infrastructure.config_loader import load_config


class SemanticSearcher:
    """
    Handles semantic search queries by delegating to the appropriate
    vector database backend, and implements advanced RAG techniques:
    Query Expansion and Cross-Encoder Re-ranking.
    """

    def __init__(self):
        """Initializes the searcher, configuration, and advanced models."""
        self.cfg = load_config()
        self.db_mode = self.cfg.get("database", {}).get("mode", "sqlite")

        # Initialize Re-ranker lazily to save memory if not immediately used
        self.reranker = None

    def _expand_query(self, query: str) -> list[str]:
        """Uses LLM to expand the query to catch synonyms and different phrasings."""
        import litellm

        print(f"Expanding query: '{query}'...")
        prompt = f"Expand the following search query into 3 similar but distinct semantic queries to improve database retrieval. Output exactly one query per line, no bullet points, no extra text. Original query: {query}"

        from src.infrastructure.config_loader import resolve_utility_llm

        model, api_key = resolve_utility_llm(self.cfg)
        if not api_key:
            # Fallback to single query if no provider API key is available
            return [query]

        try:
            from src.core.transport_retry import call_with_transport_retry
            timeout = self.cfg.get("llm_timeout", 600.0)
            retries = self.cfg.get("payload_pipeline", {}).get("transport_retries", 2)
            backoff = self.cfg.get("payload_pipeline", {}).get("transport_backoff", 2.0)

            response = call_with_transport_retry(
                lambda: litellm.completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    api_key=api_key,
                    timeout=timeout,
                ),
                retries=retries,
                backoff=backoff,
                model=model,
            )
            content = response.choices[0].message.content.strip()
            queries = [q.strip() for q in content.split("\n") if q.strip()]
            return queries[:3] + [query]
        except Exception as e:
            print(f"Query expansion failed: {e}. Proceeding with original query.")
            return [query]

    def _rerank_results(self, query: str, results: list) -> list:
        """Uses a Cross-Encoder to re-rank retrieved documents."""
        if not results:
            return results

        if self.reranker is None:
            from sentence_transformers import CrossEncoder

            # BGE/MS-Marco style lightweight cross-encoder for local re-ranking
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        print("Re-ranking results with Cross-Encoder...")

        # Prepare pairs of (query, document_content)
        # Results structure is [(content, source, distance), ...]
        pairs = [[query, row[0]] for row in results]

        # Predict relevance scores
        scores = self.reranker.predict(pairs)

        # Attach scores and sort (higher is better for CrossEncoder)
        scored_results = []
        for i, score in enumerate(scores):
            # Repackage as (content, source, rerank_score)
            scored_results.append((results[i][0], results[i][1], float(score)))

        scored_results.sort(key=lambda x: x[2], reverse=True)
        return scored_results

    def search(self, query: str, n_results: int = 3):
        """
        Executes an advanced semantic search.
        """
        print(
            f"\nInitiating Advanced Search for: '{query}' using {self.db_mode} backend...\n"
        )

        from src.infrastructure.vector_store_factory import VectorStoreFactory

        store = VectorStoreFactory.get_store()

        # Step 1: Query Expansion
        expanded_queries = self._expand_query(query)
        print(f"Expanded Queries: {expanded_queries}\n")

        # Step 2: Retrieve from Vector DB (Oversample by fetching more results)
        raw_results = []
        seen_contents = set()

        for q in expanded_queries:
            # Oversample: fetch 5 per query instead of 3
            res = store.query(q, n_results=5)
            for row in res:
                content = row[0]
                if content not in seen_contents:
                    seen_contents.add(content)
                    raw_results.append(row)

        if not raw_results:
            print("No relevant results found.")
            return []

        # Step 3: Re-rank using Cross-Encoder
        reranked_results = self._rerank_results(query, raw_results)

        # Step 4: Truncate to final top N
        final_results = reranked_results[:n_results]

        from src.core.context_sanitizer import ContextSanitizer
        sanitizer = ContextSanitizer()

        sanitized_results = []
        for i, row in enumerate(final_results):
            content, source, score = row
            clean_content = sanitizer.sanitize(content)
            text = clean_content[:300] + "..."
            print(f"[{i+1}] Source: {source} (Re-rank Score: {score:.4f})")
            print(f"Snippet: {text}\n")
            sanitized_results.append((clean_content, source, score))

        return sanitized_results


def main():
    if len(sys.argv) < 2:
        print("Usage: semantic_search.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    searcher = SemanticSearcher()
    searcher.search(query)


if __name__ == "__main__":
    main()
