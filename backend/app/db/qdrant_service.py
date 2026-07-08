from typing import Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointIdSelector,
    PointStruct,
    VectorParams,
)

from app.core.config import settings
from app.db.vector_store import VectorStore


class QdrantService(VectorStore):

    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        self.collection_name = settings.qdrant_collection

    async def health_check(self) -> bool:
        try:
            await self.client.get_collections()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Qdrant: {e}")

    async def ensure_collection(self, collection_name: str) -> None:
        collections = await self.client.get_collections()
        existing = {c.name for c in collections.collections}
        if collection_name not in existing:
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE,
                ),
            )

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
        point = PointStruct(
            id=memory_id,
            vector=vector,
            payload={
                "text": text,
                "category": category,
                "user_id": user_id,
                "agent_id": agent_id,
                "status": status,
            },
        )
        await self.client.upsert(collection_name=self.collection_name, points=[point])

    async def search(
        self,
        query_vector: list[float],
        user_id: str,
        agent_id: Optional[str],
        top_k: int = 5,
    ) -> list[dict]:
        must_conditions = [
            FieldCondition(key="user_id", match=MatchValue(value=user_id)),
            FieldCondition(key="status", match=MatchValue(value="active")),
        ]
        if agent_id is not None:
            must_conditions.append(
                FieldCondition(key="agent_id", match=MatchValue(value=agent_id))
            )

        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=Filter(must=must_conditions),
            with_payload=True,
            limit=top_k,
        )
        return [
            {
                "id": str(result.id),
                "score": result.score,
                "text": result.payload.get("text", ""),
                "category": result.payload.get("category", ""),
            }
            for result in results
        ]

    async def delete(self, memory_id: str) -> None:
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdSelector(points=[memory_id]),
        )

    async def close(self) -> None:
        await self.client.close()
