#!/usr/bin/env python3
import os
import math

def split_file(filepath, max_lines=500):
    with open(filepath, "r", encoding="utf8") as f:
        lines = f.readlines()
        
    if len(lines) <= max_lines:
        return False
        
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    num_parts = math.ceil(len(lines) / max_lines)
    for i in range(num_parts):
        part_lines = lines[i * max_lines : (i + 1) * max_lines]
        part_name = f"{name}_part{i + 1}{ext}"
        part_path = os.path.join(directory, part_name)
        with open(part_path, "w", encoding="utf8") as f:
            f.writelines(part_lines)
            
    os.remove(filepath)
    print(f"Split {filename} into {num_parts} optimized chunks.")
    return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    exclude_files = ["README.md", "change_log.md", "GEMINI.md", "USER_PROFILE.md"]
    
    print("Scanning library for oversized markdown files...")
    for root, dirs, files in os.walk(repo_root):
        if ".git" in root or ".agents" in root:
            continue
        for file in files:
            if file.endswith(".md") and file not in exclude_files:
                filepath = os.path.join(root, file)
                split_file(filepath)

if __name__ == "__main__":
    main()
