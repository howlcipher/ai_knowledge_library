#!/usr/bin/env python3
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    profile_path = os.path.join(repo_root, "USER_PROFILE.md")
    summary_path = os.path.join(repo_root, ".agents", "rules", "user_summary.md")
    
    if not os.path.exists(profile_path):
        print("Profile not found.")
        return
        
    summary = [
        "---\n",
        "name: user_summary\n",
        "description: Condensed user profile for quick context injection.\n",
        "---\n",
        "User is William Elias, a Software Engineer specializing in Cyber Defense.\n",
        "Core capabilities include Python, Go, Docker, and secure Cloud architecture.\n"
    ]
    
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w") as f:
        f.writelines(summary)
        
    print("Agent summary generated at .agents/rules/user_summary.md")

if __name__ == "__main__":
    main()
