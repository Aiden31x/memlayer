from abc import ABC, abstractmethod
from typing import Optional


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    async def ensure_collection(self, collection_name: str) -> None:
        """Ensure that the collection exists."""
        pass

    @abstractmethod
    async def upsert(
        self,
        memory_id: str,
        vector: list[float],
        text: str,
        category: str,
        user_id: str,
        agent_id: Optional[str],
        status: str,
    ) -> None:
        """Upsert a memory into the vector store."""
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        user_id: str,
        agent_id: Optional[str],
        top_k: int = 5,
    ) -> list[dict]:
        """Search the vector store for the most similar memories.

        Each result dict contains: id, score, text, category.
        """
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        """Delete a memory from the vector store."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the vector store."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check the health of the vector store."""
        pass
