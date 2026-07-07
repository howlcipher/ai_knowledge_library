#!/usr/bin/env python3
import os
import sys

def prompt_user_details():
    print("Please enter the details for the new profile.")
    name = input("Full Name: ").strip()
    email = input("Email: ").strip()
    linkedin = input("LinkedIn URL (optional): ").strip()
    github = input("GitHub Username (optional): ").strip()
    return name, email, linkedin, github

def create_profile_content(name, email, linkedin, github):
    content = [
        f"# {name} User Profile\n",
        "## Contact and Links",
        f"* Email: {email}"
    ]
    if linkedin:
        content.append(f"* LinkedIn: {linkedin}")
    if github:
        content.append(f"* GitHub: github.com/{github}")
        
    content.extend([
        "",
        "## Professional Summary",
        "Add your professional summary here.",
        "",
        "## Core Skills",
        "* Add your core skills here.",
        "",
        "## Professional Experience",
        "* Add your experience here.",
        "",
        "## Education and Certifications",
        "* Add your education here."
    ])
    
    return "\n".join(content) + "\n"

def main():
    print("Welcome to the AI Knowledge Library Profile Setup")
    print("1. Keep the original William Elias profile and add a new one.")
    print("2. Remove the William Elias profile entirely and create your own.")
    print("3. Exit without making changes.")
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    default_profile = os.path.join(repo_root, "USER_PROFILE.md")
    
    if choice == '1':
        name, email, linkedin, github = prompt_user_details()
        safe_name = name.replace(" ", "_").lower()
        new_profile_path = os.path.join(repo_root, f"USER_PROFILE_{safe_name}.md")
        
        with open(new_profile_path, 'w') as f:
            f.write(create_profile_content(name, email, linkedin, github))
            
        print(f"Created new profile at USER_PROFILE_{safe_name}.md")
        print("Original profile kept intact.")
        
    elif choice == '2':
        name, email, linkedin, github = prompt_user_details()
        
        if os.path.exists(default_profile):
            os.remove(default_profile)
            print("Removed default USER_PROFILE.md")
            
        with open(default_profile, 'w') as f:
            f.write(create_profile_content(name, email, linkedin, github))
            
        print(f"Created your new primary profile at USER_PROFILE.md")
        
    else:
        print("Exiting without changes.")

if __name__ == "__main__":
    main()
