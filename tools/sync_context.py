#!/usr/bin/env python3
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    index_path = os.path.join(repo_root, "documentation", "master_index.md")
    
    with open(index_path, "w") as index_file:
        index_file.write("# Master Library Index\n\n")
        for root, dirs, files in os.walk(repo_root):
            if ".git" in root or ".agents" in root:
                continue
            for file in files:
                if file.endswith(".md"):
                    rel_path = os.path.relpath(os.path.join(root, file), repo_root)
                    index_file.write(f"* {rel_path}\n")
                    
    print("Master index generated successfully at documentation/master_index.md")

if __name__ == "__main__":
    main()
