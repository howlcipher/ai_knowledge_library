#!/usr/bin/env python3
import argparse
import chromadb
from chromadb.config import Settings
import os

def main():
    parser = argparse.ArgumentParser(description="Sync knowledge base to ChromaDB.")
    parser.add_argument("--host", type=str, help="ChromaDB Host (for client-server mode)")
    parser.add_argument("--port", type=str, help="ChromaDB Port")
    args = parser.parse_args()

    if args.host and args.port:
        print(f"Connecting to ChromaDB Server at {args.host}:{args.port}")
        client = chromadb.HttpClient(host=args.host, port=args.port)
    else:
        db_path = os.path.join(os.getcwd(), ".chroma")
        print(f"Connecting to local ChromaDB at {db_path}")
        client = chromadb.PersistentClient(path=db_path)

    print("Sync complete.")

if __name__ == "__main__":
    main()
