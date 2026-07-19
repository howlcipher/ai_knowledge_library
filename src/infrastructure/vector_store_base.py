from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class BaseVectorStore(ABC):
    """Abstract base class for vector database backends."""

    @abstractmethod
    def init_db(self) -> None:
        """Initialize the database (e.g. creating tables/extensions)."""

    @abstractmethod
    def reset(self) -> None:
        """
        Remove all previously indexed documents so a full rebuild starts from
        an empty store. Rebuilds must be idempotent: without a reset, chunk
        ids that disappear from the scan (file shrank, moved, or was deleted)
        would survive every subsequent upsert.
        """

    @abstractmethod
    def upsert(
        self, docs: List[str], metadatas: List[Dict], ids: Optional[List[str]] = None
    ) -> None:
        """
        Upsert documents into the vector store.
        """

    @abstractmethod
    def query(self, text: str, n_results: int = 5) -> List[Tuple[str, str, float]]:
        """
        Query the vector store for similar documents.
        Returns:
            A list of tuples: (content, source, distance).
        """
