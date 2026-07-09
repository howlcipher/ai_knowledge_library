from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional

class BaseVectorStore(ABC):
    """Abstract base class for vector database backends."""
    
    @abstractmethod
    def init_db(self) -> None:
        """Initialize the database (e.g. creating tables/extensions)."""
        pass

    @abstractmethod
    def upsert(self, docs: List[str], metadatas: List[Dict], ids: Optional[List[str]] = None) -> None:
        """
        Upsert documents into the vector store.
        """
        pass

    @abstractmethod
    def query(self, text: str, n_results: int = 5) -> List[Tuple[str, str, float]]:
        """
        Query the vector store for similar documents.
        Returns:
            A list of tuples: (content, source, distance).
        """
        pass
