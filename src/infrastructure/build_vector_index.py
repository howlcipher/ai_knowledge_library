#!/usr/bin/env python3
"""
Vector Index Builder Tool.

This module provides an object oriented approach to building a vector database
index from the markdown documentation in the repository. It chunks the text
and stores it in the configured vector store.
"""

import glob
import os

try:
    pass
except ImportError:
    pass


# Removed boilerplate

from src.infrastructure.config_loader import load_config


class TextChunker:
    """
    Helper class responsible for chunking text content.
    """

    def __init__(self, max_len: int = 1000):
        """
        Args:
            max_len (int): Maximum character length per chunk.
        """
        self.max_len = max_len

    def chunk_text(self, text: str) -> list:
        """
        Splits text into smaller chunks based on word count and max length.

        Args:
            text (str): The input text to chunk.

        Returns:
            list: A list of text chunks.
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_len = 0

        for word in words:
            if current_len + len(word) > self.max_len:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_len = len(word)
            else:
                current_chunk.append(word)
                current_len += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


class VectorIndexBuilder:
    """
    Manages the indexing of markdown files into the configured vector store.
    """

    def __init__(self):
        """
        Initializes the index builder, loading configuration and setting up chunking.
        """
        from src.infrastructure.config_loader import default_loader

        self.repo_root = default_loader.get_repo_root()
        self.cfg = load_config()
        self.db_mode = self.cfg.get("database", {}).get("mode", "sqlite")

        # Load indexing config
        self.index_config = self.cfg.get("indexing", {})
        self.max_chunk_len = self.index_config.get("max_chunk_length", 1000)
        self.batch_size = self.index_config.get("batch_size", 100)
        self.collection_name = self.index_config.get(
            "collection_name", "ai_library_knowledge"
        )

        self.chunker = TextChunker(max_len=self.max_chunk_len)

        self.docs_to_insert = []
        self.metadata_to_insert = []
        self.ids_to_insert = []

    def _should_skip_file(self, file_path: str) -> bool:
        """
        Determines whether a given file path should be skipped during indexing.

        Args:
            file_path (str): The absolute path to the file.

        Returns:
            bool: True if the file should be skipped, False otherwise.
        """
        if ".git" in file_path or (
            ".agents" not in file_path
            and "documentation" not in file_path
            and "README" not in file_path
        ):
            return True
        return False

    def scan_files(self):
        """
        Scans the repository for markdown files, reads them, and prepares chunks.
        """
        print("Scanning for markdown files...")
        md_files = glob.glob(os.path.join(self.repo_root, "**", "*.md"), recursive=True)

        for file_path in md_files:
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf8") as f:
                    content = f.read()
                    if not content.strip():
                        continue

                    rel_path = os.path.relpath(file_path, self.repo_root)
                    chunks = self.chunker.chunk_text(content)

                    for i, chunk in enumerate(chunks):
                        self.docs_to_insert.append(chunk)
                        self.metadata_to_insert.append({"source": rel_path, "chunk": i})
                        self.ids_to_insert.append(f"{rel_path}_{i}")

            except Exception as e:
                print(f"Skipping {file_path}: {e}")

    def insert_chunks(self):
        """
        Inserts the processed chunks into the configured database.
        """
        if not self.docs_to_insert:
            print("No markdown content found to index.")
            return

        print(
            f"Inserting {len(self.docs_to_insert)} chunks into {self.db_mode} database..."
        )

        from src.infrastructure.vector_store_factory import VectorStoreFactory

        store = VectorStoreFactory.get_store()
        store.init_db()

        for i in range(0, len(self.docs_to_insert), self.batch_size):
            store.upsert(
                docs=self.docs_to_insert[i : i + self.batch_size],
                metadatas=self.metadata_to_insert[i : i + self.batch_size],
                ids=self.ids_to_insert[i : i + self.batch_size],
            )

        print("Knowledge base indexing complete!")

    def run(self):
        """
        Executes the entire indexing pipeline.
        """
        self.scan_files()
        self.insert_chunks()


def main():
    """
    Main entry point for the vector indexing script.
    """
    builder = VectorIndexBuilder()
    builder.run()


if __name__ == "__main__":
    main()
