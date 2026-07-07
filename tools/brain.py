#!/usr/bin/env python3
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/brain.py <search_term>")
        return
        
    term = sys.argv[1].lower()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    print(f"Searching library for: {term}")
    
    found = False
    for root, dirs, files in os.walk(repo_root):
        if ".git" in root or ".agents" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf8") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if term in line.lower():
                                rel_path = os.path.relpath(filepath, repo_root)
                                print(f"[{rel_path} Line {i + 1}] {line.strip()}")
                                found = True
                except Exception:
                    pass
                    
    if not found:
        print("No results found.")

if __name__ == "__main__":
    main()
