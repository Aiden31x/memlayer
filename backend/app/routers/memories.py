from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.schemas import (
    AddMemoryResponse,
    ConversationRequest,
    GetMemoriesResponse,
)
from app.services.extraction import ExtractionService
from app.services.resolution import ResolutionService
from app.services.retrieval import RetrievalService
from app.services.storage import StorageService

router = APIRouter(prefix="/memories", tags=["memories"])

extraction_service = ExtractionService()
resolution_service = ResolutionService()
storage_service = StorageService()
retrieval_service = RetrievalService()


@router.post("/", response_model=AddMemoryResponse)
async def create_memory(
    request: ConversationRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    vector_store = req.app.state.vector_store

    facts = await extraction_service.extract_facts(request)
    operations = await resolution_service.resolve(
        facts=facts.facts,
        user_id=request.user_id,
        agent_id=request.agent_id,
        vector_store=vector_store,
    )
    saved = await storage_service.store(
        operations=operations,
        user_id=request.user_id,
        agent_id=request.agent_id,
        db=db,
        vector_store=vector_store,
    )
    return AddMemoryResponse(memories=saved)


@router.get("/", response_model=GetMemoriesResponse)
async def get_memories(
    user_id: str,
    query: str,
    req: Request,
    agent_id: Optional[str] = None,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db),
):
    vector_store = req.app.state.vector_store

    memories = await retrieval_service.search(
        query=query,
        user_id=user_id,
        agent_id=agent_id,
        db=db,
        vector_store=vector_store,
        top_k=top_k,
    )
    return GetMemoriesResponse(memories=memories)
