#!/usr/bin/env python3
"""
webhook_server.py

Provides a FastAPI-based server for handling incoming webhooks
(e.g., from GitHub) and triggering background synchronization of the knowledge graph.
"""

import os
import sys
import subprocess
from fastapi import FastAPI, Request, HTTPException

# Ensure project root is in the path for module loading
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
if repo_root not in sys.path:
    sys.path.append(repo_root)

from config.loader import load_config


class WebhookServer:
    """
    Manages the FastAPI application and webhook routes.
    Encapsulates configuration and dependency management.
    """

    def __init__(self):
        """Initializes the server application and loads configuration."""
        self.app = FastAPI(title="AI Knowledge Library Webhook Server")
        self.cfg = load_config()
        self.expected_secret = self.cfg.get("server", {}).get("webhook_secret", "")
        self.host = self.cfg.get("server", {}).get("host", "0.0.0.0")  # nosec B104
        self.port = self.cfg.get("server", {}).get("port", 8000)

        # Register routes
        self._setup_routes()

    def _setup_routes(self):
        """Registers all HTTP routes for the FastAPI app."""

        @self.app.post("/webhook/sync")
        async def trigger_sync(request: Request):
            return await self._handle_sync_request(request)

    async def _handle_sync_request(self, request: Request):
        """
        Validates the incoming webhook payload and triggers the sync process.
        """
        if self.expected_secret:
            provided_secret = request.headers.get("X-Webhook-Secret")
            if provided_secret != self.expected_secret:
                raise HTTPException(status_code=403, detail="Invalid webhook secret")

        print("Webhook received! Triggering context synchronization...")
        try:
            # Execute the sync tool asynchronously as a subprocess
            subprocess.Popen(["python3", "tools/sync_context.py"])
            return {"status": "success", "message": "Sync triggered in background"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run(self):
        """Starts the Uvicorn ASGI server."""
        import uvicorn

        uvicorn.run(self.app, host=self.host, port=self.port)


def main():
    server = WebhookServer()
    server.run()


if __name__ == "__main__":
    main()
