import os
import sys

def init_workspace(project_name):
    if not project_name.isalnum():
        print("Error: Name must be alphanumeric")
        sys.exit(1)
        
    base_path = os.path.join(os.getcwd(), project_name, ".agents", "skills")
    os.makedirs(base_path, exist_ok=True)
    
    anchor_file = os.path.join(base_path, "WORKSPACE_RULES.md")
    with open(anchor_file, "w") as file_out:
        file_out.write("name: workspace_anchor\ndescription: Triggers on all operations to ground the agent\n\n# Project Rules\n\n* Follow all global structural and formatting standards.\n")
        
    print(f"Workspace telemetry successfully built at: {base_path}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "new_project"
    init_workspace(target)\n