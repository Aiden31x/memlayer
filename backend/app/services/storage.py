import uuid
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory
from app.db.vector_store import VectorStore
from app.models.schemas import MemoryRecord
from app.services.embeddings import EmbeddingsService
from app.services.resolution import ResolutionOperation


class StorageService:

    async def store(
        self,
        operations: list[ResolutionOperation],
        user_id: str,
        agent_id: Optional[str],
        db: AsyncSession,
        vector_store: VectorStore,
    ) -> list[MemoryRecord]:
        """
        Execute a list of ResolutionOperations against Postgres and Qdrant.

        ADD       — insert new Memory row + upsert vector.
        SUPERSEDE — insert new row, mark old row superseded in both stores.
        NOOP      — skip.

        Returns MemoryRecord for every row that was written (ADD + SUPERSEDE new rows).
        """
        saved: list[MemoryRecord] = []

        for op in operations:
            if op.operation == "NOOP":
                continue

            new_id = uuid.uuid4()
            vector = EmbeddingsService.embed_text(op.fact_text)

            # --- Postgres: insert the new memory row ---
            new_memory = Memory(
                id=new_id,
                user_id=user_id,
                agent_id=agent_id,
                text=op.fact_text,
                category=op.fact.category,
                status="active",
                confidence=op.fact.confidence,
            )
            db.add(new_memory)

            # --- Qdrant: upsert the new vector ---
            await vector_store.upsert(
                memory_id=str(new_id),
                vector=vector,
                text=op.fact_text,
                category=op.fact.category,
                user_id=user_id,
                agent_id=agent_id,
                status="active",
            )

            if op.operation == "SUPERSEDE" and op.supersedes_id:
                old_id = uuid.UUID(op.supersedes_id)

                # Postgres: mark the old row superseded and point it to the new one
                await db.execute(
                    update(Memory)
                    .where(Memory.id == old_id)
                    .values(status="superseded", superseded_by=new_id)
                )

                # Qdrant: flip the old point's status payload
                await vector_store.update_status(op.supersedes_id, "superseded")

            saved.append(MemoryRecord.model_validate(new_memory))

        await db.commit()
        return saved
