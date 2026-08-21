#!/usr/bin/env python3
"""
mcp_server.py

Exposes the HowlPlane Knowledge and Semantic Search backend as a Model Context Protocol (MCP) server.
This allows any MCP-compatible agent to securely search the library, with all data routed
through the ContextSanitizer.
"""

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp.server import FastMCP  # type: ignore
    except ImportError:
        FastMCP = None

from src.infrastructure.semantic_search import SemanticSearcher
from src.core.context_sanitizer import format_safe_prompt

def _noop_tool_decorator(*args, **kwargs):
    def _wrapper(fn):
        return fn
    return _wrapper

# Initialize the MCP Server if available
mcp = FastMCP("HowlPlane") if FastMCP is not None else None
tool_decorator = mcp.tool() if mcp is not None else _noop_tool_decorator()

@tool_decorator
def search_knowledge_library(query: str, n_results: int = 5) -> str:
    """
    Search the HowlPlane knowledge base for context related to a query.
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

        cleaned_chunks = [f"Source: {src}\n{c.strip()}" for c, src, _ in results]

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
    if mcp is not None:
        mcp.run(transport='stdio')
