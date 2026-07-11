#!/usr/bin/env python3
"""
mcp_client.py

Provides a robust, synchronous wrapper around the asynchronous Model Context Protocol (MCP) SDK.
This allows synchronous components like orchestrator.py to dynamically load and interact with 
external MCP plugins (like GitHub, Slack, etc.) without requiring a massive async rewrite.
"""

import asyncio
import threading
from typing import Dict, Any, List

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


class SyncMCPClient:
    """
    A synchronous client for an MCP server running over stdio.
    Maintains a background event loop to handle continuous communication.
    """
    def __init__(self, name: str, command: str, args: List[str], env: Dict[str, str] = None):
        self.name = name
        self.server_params = StdioServerParameters(command=command, args=args, env=env)
        self.session = None
        self._exit_stack = None
        
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._start_loop, daemon=True, name=f"MCP-Thread-{name}")
        self._thread.start()
        
    def _start_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_coro(self, coro):
        """Helper to run async code synchronously from the main thread."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    async def _initialize(self):
        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()
        read, write = await self._exit_stack.enter_async_context(stdio_client(self.server_params))
        self.session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    def connect(self):
        """Establish the connection to the MCP server."""
        self._run_coro(self._initialize())

    def get_tools(self) -> List[Any]:
        """Fetch all available tools from the server."""
        async def _get():
            result = await self.session.list_tools()
            return result.tools
        return self._run_coro(_get())
        
    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a specific tool securely on the remote server."""
        async def _call():
            result = await self.session.call_tool(tool_name, arguments)
            return result
        return self._run_coro(_call())

    def close(self):
        """Clean up resources."""
        async def _close():
            if self._exit_stack:
                await self._exit_stack.aclose()
        self._run_coro(_close())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=2.0)

