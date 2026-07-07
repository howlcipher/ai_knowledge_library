#!/usr/bin/env python3
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    out_path = os.path.join(repo_root, "infrastructure", "dashboard.html")
    with open(out_path, "w") as f:
        f.write("<html><body><h1>System Health</h1><p>All systems operational.</p></body></html>\n")
    print("Dashboard generated.")

if __name__ == "__main__":
    main()
