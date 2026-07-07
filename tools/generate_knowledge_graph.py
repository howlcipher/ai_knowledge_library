#!/usr/bin/env python3
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    out_path = os.path.join(repo_root, "documentation", "knowledge_graph.md")
    
    arrow = chr(45) + chr(45) + ">"
    
    with open(out_path, "w") as f:
        f.write("# Library Knowledge Graph\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")
        f.write("    Root[AI Knowledge Library]\n")
        
        for root, dirs, files in os.walk(repo_root):
            if ".git" in root or ".agents" in root:
                continue
            if root == repo_root:
                for directory in dirs:
                    f.write(f"    Root {arrow} {directory}[{directory}]\n")
                
        f.write("```\n")
        
    print("Knowledge graph generated successfully.")

if __name__ == "__main__":
    main()
