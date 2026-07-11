#!/usr/bin/env python3
"""
mcp_server.py

Exposes the AI Knowledge Library and Semantic Search backend as a Model Context Protocol (MCP) server.
This allows any MCP-compatible agent to securely search the library, with all data routed
through the ContextSanitizer.
"""

from mcp.server.fastmcp import FastMCP
from src.infrastructure.semantic_search import SemanticSearcher
from src.core.context_sanitizer import format_safe_prompt

# Initialize the MCP Server
mcp = FastMCP("AI_Knowledge_Library")

@mcp.tool()
def search_knowledge_library(query: str, n_results: int = 5) -> str:
    """
    Search the AI knowledge library for context related to a query.
    All retrieved data is strictly sanitized to prevent prompt injections.
    
    Args:
        query: The search term or question to look for in the library.
        n_results: Maximum number of snippets to return (default 5).
    """
    try:
        searcher = SemanticSearcher()
        # searcher.search natively uses ContextSanitizer now
        results = searcher.search(query, n_results=n_results)

        if not results:
            return "No relevant context found in the library."

        cleaned_chunks = []
        for result in results:
            content, source, score = result
            chunk = f"Source: {source}\n{content.strip()}"
            cleaned_chunks.append(chunk)

        safe_output = format_safe_prompt(
            system_instruction="The following are results from the knowledge library semantic search tool.",
            user_query=query,
            cleaned_chunks=cleaned_chunks
        )
        
        return safe_output
        
    except Exception as e:
        return f"Error executing semantic search: {str(e)}"

if __name__ == "__main__":
    # Standard MCP initialization over stdio
    mcp.run(transport='stdio')
