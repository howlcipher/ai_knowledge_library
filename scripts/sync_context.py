import os
import sys
import shutil


def link_skills():
    home = os.path.expanduser("~")
    central_dir = os.path.join(
        home, "projects", "ai_knowledge_library", ".agents", "skills"
    )
    target_dir = os.path.join(os.getcwd(), ".agents", "skills")

    if not os.path.exists(central_dir):
        print("Error: Central library path not found")
        sys.exit(1)

    os.makedirs(target_dir, exist_ok=True)

    for item in os.listdir(central_dir):
        source_item = os.path.join(central_dir, item)
        if os.path.isdir(source_item):
            target_item = os.path.join(target_dir, item)
            if os.path.exists(target_item):
                if os.path.islink(target_item):
                    os.unlink(target_item)
                else:
                    shutil.rmtree(target_item)
            os.symlink(source_item, target_item)
            print(f"Mapped context layer: {item}")


if __name__ == "__main__":
    link_skills()
