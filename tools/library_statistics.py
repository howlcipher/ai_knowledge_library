#!/usr/bin/env python3
import os
import re

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Count files
    file_count = 0
    for root, _, files in os.walk(repo_root):
        if '.git' in root:
            continue
        file_count += len(files)
        
    # Read README
    readme_path = os.path.join(repo_root, "README.md")
    with open(readme_path, "r") as f:
        content = f.read()
        
    # Replace or add the badge
    badge_pattern = r'<img src="https://img\.shields\.io/static/v1\?label=Library_Size&message=\d+&color=success&style=for_the_badge" alt="Library Size Badge" />'
    new_badge = f'<img src="https://img.shields.io/static/v1?label=Library_Size&message={file_count}&color=success&style=for_the_badge" alt="Library Size Badge" />'
    
    if re.search(badge_pattern, content):
        content = re.sub(badge_pattern, new_badge, content)
    else:
        # insert after the first badge line
        first_badge_line = '<img src="https://img.shields.io/static/v1?label=AI&message=Knowledge_Library&color=blueviolet&style=for_the_badge" alt="AI Library Badge" />'
        content = content.replace(first_badge_line, f"{first_badge_line}\n  {new_badge}")
        
    with open(readme_path, "w") as f:
        f.write(content)
        
    print(f"Library statistics generated: {file_count} files counted. README updated.")

if __name__ == "__main__":
    main()
