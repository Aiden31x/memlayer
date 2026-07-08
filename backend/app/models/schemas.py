import uuid
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str


class ConversationRequest(BaseModel):
    user_id: str
    agent_id: Optional[str] = None
    messages: List[Message]


class ExtractedFact(BaseModel):
    category: str
    key: str
    value: str
    confidence: float
    evidence: str


class ExtractionResponse(BaseModel):
    facts: List[ExtractedFact]


# --- Storage / retrieval schemas ---

class MemoryRecord(BaseModel):
    id: uuid.UUID
    user_id: str
    agent_id: Optional[str]
    text: str
    category: str
    status: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


class AddMemoryResponse(BaseModel):
    memories: List[MemoryRecord]


class GetMemoriesResponse(BaseModel):
    memories: List[MemoryRecord]