import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory
from app.db.vector_store import VectorStore
from app.models.schemas import MemoryRecord
from app.services.embeddings import EmbeddingsService


class RetrievalService:

    async def search(
        self,
        query: str,
        user_id: str,
        agent_id: Optional[str],
        db: AsyncSession,
        vector_store: VectorStore,
        top_k: int = 5,
    ) -> list[MemoryRecord]:
        """
        Embed the query, search Qdrant for the closest active memories scoped to
        this user/agent, then hydrate full rows from Postgres in score order.
        """
        query_vector = EmbeddingsService.embed_text(query)

        hits = await vector_store.search(
            query_vector=query_vector,
            user_id=user_id,
            agent_id=agent_id,
            top_k=top_k,
        )

        if not hits:
            return []

        # Preserve the relevance order returned by Qdrant
        hit_ids = [uuid.UUID(h["id"]) for h in hits]
        score_by_id = {h["id"]: h["score"] for h in hits}

        result = await db.execute(
            select(Memory).where(Memory.id.in_(hit_ids))
        )
        rows = result.scalars().all()

        # Sort by Qdrant score (descending) since SQL IN() doesn't preserve order
        rows_sorted = sorted(rows, key=lambda r: score_by_id.get(str(r.id), 0), reverse=True)

        return [MemoryRecord.model_validate(r) for r in rows_sorted]
