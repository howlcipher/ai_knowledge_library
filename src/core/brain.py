#!/usr/bin/env python3
"""
Library Search Tool (Brain).

This module provides an object-oriented search functionality across the
library files. It delegates to the SemanticSearcher to utilize the vector
database infrastructure for advanced RAG queries.
"""

import argparse
import sys

from src.infrastructure.semantic_search import SemanticSearcher


class LibrarySearcher:
    """
    Handles searching for specific terms within the library files by
    delegating to the SemanticSearcher vector database backend.
    """

    def __init__(self, search_term: str):
        """
        Initializes the LibrarySearcher with a search term.

        Args:
            search_term (str): The term to search for.
        """
        self.search_term = search_term

    def search(self):
        """
        Executes the search across the repository utilizing the vector DB.
        """
        print(f"Searching library semantically for: {self.search_term}\n")
        try:
            searcher = SemanticSearcher()
            results = searcher.search(self.search_term, n_results=5)

            if not results:
                print("No results found.")
                return

            from src.core.context_sanitizer import format_safe_prompt
            
            cleaned_chunks = []
            for result in results:
                content, source, score = result
                chunk = f"Source: {source}\n{content.strip()}"
                cleaned_chunks.append(chunk)

            safe_output = format_safe_prompt(
                system_instruction="The following are results from your semantic search tool.",
                user_query=self.search_term,
                cleaned_chunks=cleaned_chunks
            )
            print(safe_output)

        except Exception as e:
            print(f"Error during semantic search: {e}", file=sys.stderr)


def main():
    """
    CLI entry point for testing the brain search script standalone.
    """
    parser = argparse.ArgumentParser(description="AI Knowledge Library Search (Brain)")
    parser.add_argument(
        "query", type=str, help="The search query to look for in the library"
    )

    args = parser.parse_args()
    searcher = LibrarySearcher(args.query)
    searcher.search()


if __name__ == "__main__":
    main()
