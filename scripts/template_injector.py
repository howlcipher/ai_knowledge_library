#!/usr/bin/env python3
import os
import re

def inject_profile_to_skills():
    profile_path = "USER_PROFILE.md"
    skills_dir = ".agents/skills"
    
    if not os.path.exists(profile_path):
        print("USER_PROFILE.md not found. Skipping dynamic templating.")
        return
        
    with open(profile_path, 'r') as f:
        profile_content = f.read()
        
    # Extract name
    name_match = re.search(r'# (.+) User Profile', profile_content)
    user_name = name_match.group(1) if name_match else "User"
    
    for root, _, files in os.walk(skills_dir):
        for file in files:
            if file == "SKILL.md":
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                    
                if "{{USER_NAME}}" in content:
                    content = content.replace("{{USER_NAME}}", user_name)
                    with open(path, 'w') as f:
                        f.write(content)
                        
    print("Dynamically injected USER_PROFILE.md variables into SKILL.md templates.")

if __name__ == "__main__":
    inject_profile_to_skills()
