#!/usr/bin/env python3
import sys
import os
import subprocess
from fastapi import FastAPI, Request, HTTPException

# Add the project root to sys.path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.loader import load_config

app = FastAPI(title="AI Knowledge Library Webhook Server")
cfg = load_config()

@app.post("/webhook/sync")
async def trigger_sync(request: Request):
    expected_secret = cfg.get("server", {}).get("webhook_secret", "")
    
    # Check X-Webhook-Secret header if configured
    if expected_secret:
        provided_secret = request.headers.get("X-Webhook-Secret")
        if provided_secret != expected_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

    print("Webhook received! Triggering context synchronization...")
    try:
        subprocess.Popen(["python3", "tools/sync_context.py"])
        return {"status": "success", "message": "Sync triggered in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    import uvicorn
    host = cfg.get("server", {}).get("host", "0.0.0.0")
    port = cfg.get("server", {}).get("port", 8000)
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
