from dataclasses import dataclass, field
from typing import Literal, Optional

from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel, TypeAdapter

from app.core.config import settings
from app.db.vector_store import VectorStore
from app.models.schemas import ExtractedFact
from app.services.embeddings import EmbeddingsService

# Cosine similarity threshold above which we call the LLM to compare facts.
# Below this, facts are different enough that we always ADD without an LLM call.
SIMILARITY_THRESHOLD = 0.82

_genai_client = genai.Client(api_key=settings.google_api_key)
_decision_adapter = TypeAdapter(None)  # replaced below after class definition


class _ResolutionDecision(BaseModel):
    operation: Literal["ADD", "SUPERSEDE", "NOOP"]
    reason: str


_decision_adapter = TypeAdapter(_ResolutionDecision)


@dataclass
class ResolutionOperation:
    operation: Literal["ADD", "SUPERSEDE", "NOOP"]
    fact: ExtractedFact
    fact_text: str
    supersedes_id: Optional[str] = field(default=None)


class ResolutionService:

    @staticmethod
    def _fact_text(fact: ExtractedFact) -> str:
        """Canonical string stored in Postgres and embedded into Qdrant."""
        return f"{fact.key}: {fact.value}"

    @staticmethod
    async def _llm_judge(new_text: str, existing_text: str) -> _ResolutionDecision:
        """Stage 2: ask the LLM to compare a new fact against the closest existing one."""
        prompt = f"""You are deciding how a new memory fact relates to an existing stored fact.

<existing_fact>{existing_text}</existing_fact>
<new_fact>{new_text}</new_fact>

Choose exactly one operation:
- SUPERSEDE: the new fact contradicts or updates the existing one (e.g. old city → new city, old job → new job). The old fact should be marked superseded.
- NOOP: the new fact is a duplicate or strict subset of the existing one. Nothing new to store.
- ADD: the new fact is meaningfully different and should be stored alongside the existing one.

Return JSON with "operation" (one of ADD, SUPERSEDE, NOOP) and "reason" (one sentence)."""

        response = await _genai_client.aio.models.generate_content(
            model=settings.model_name,
            contents=prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_ResolutionDecision,
            ),
        )
        return _decision_adapter.validate_json(response.text)

    async def resolve(
        self,
        facts: list[ExtractedFact],
        user_id: str,
        agent_id: Optional[str],
        vector_store: VectorStore,
    ) -> list[ResolutionOperation]:
        """
        For each extracted fact:
          Stage 1 (cheap)  — embed + vector search for near-duplicates.
          Stage 2 (costly) — LLM judgment only when a close candidate is found.

        Returns one ResolutionOperation per fact.
        """
        operations: list[ResolutionOperation] = []

        for fact in facts:
            text = self._fact_text(fact)
            vector = EmbeddingsService.embed_text(text)

            candidates = await vector_store.search(
                query_vector=vector,
                user_id=user_id,
                agent_id=agent_id,
                top_k=3,
            )

            # Stage 1 filter — only candidates above the similarity threshold
            # warrant the more expensive LLM call.
            close = [c for c in candidates if c["score"] >= SIMILARITY_THRESHOLD]

            if not close:
                operations.append(ResolutionOperation(
                    operation="ADD",
                    fact=fact,
                    fact_text=text,
                ))
                continue

            # Stage 2 — compare against the single closest candidate.
            best = close[0]
            decision = await self._llm_judge(text, best["text"])

            operations.append(ResolutionOperation(
                operation=decision.operation,
                fact=fact,
                fact_text=text,
                supersedes_id=best["id"] if decision.operation == "SUPERSEDE" else None,
            ))

        return operations
