#!/usr/bin/env python3
from fastapi import FastAPI, Request, HTTPException
import subprocess
import os

app = FastAPI(title="AI Knowledge Library Webhook Server")

@app.post("/webhook/sync")
async def trigger_sync(request: Request):
    # In a real environment, validate webhook_secret here
    print("Webhook received! Triggering context synchronization...")
    try:
        subprocess.Popen(["python3", "tools/sync_context.py"])
        return {"status": "success", "message": "Sync triggered in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    import uvicorn
    # Load config in real environment
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
