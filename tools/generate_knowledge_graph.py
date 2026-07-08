#!/usr/bin/env python3
import os
from config_loader import ConfigLoader


class KnowledgeGraphGenerator:
    """
    Class responsible for generating a knowledge graph of the library structure.
    """

    def __init__(self):
        """
        Initializes the generator with configuration settings.
        """
        self.config_loader = ConfigLoader()
        self.repo_root = self.config_loader.get_repo_root()
        default_path = os.path.join(
            self.repo_root, "documentation", "knowledge_graph.md"
        )
        self.out_path = self.config_loader.get("knowledge_graph_path", default_path)
        self.arrow = chr(45) + chr(45) + ">"

    def generate_graph(self):
        """
        Traverses directories and generates a Mermaid markdown graph.
        """
        with open(self.out_path, "w") as f:
            f.write("# Library Knowledge Graph\n\n")
            f.write("```mermaid\n")
            f.write("graph TD\n")
            f.write("    Root[AI Knowledge Library]\n")

            for root, dirs, files in os.walk(self.repo_root):
                if ".git" in root or ".agents" in root:
                    continue
                if root == self.repo_root:
                    for directory in dirs:
                        f.write(f"    Root {self.arrow} {directory}[{directory}]\n")

            f.write("```\n")

        print("Knowledge graph generated successfully.")


def main():
    """
    Main function to execute the knowledge graph generator.
    """
    generator = KnowledgeGraphGenerator()
    generator.generate_graph()


if __name__ == "__main__":
    main()
