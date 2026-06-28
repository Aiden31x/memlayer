from typing import List, Literal
from pydantic import BaseModel


class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str


class ConversationRequest(BaseModel):
    messages: List[Message]


class ExtractedFact(BaseModel):
    category: str
    key: str
    value: str
    confidence: float
    evidence: str


class ExtractionResponse(BaseModel):
    facts: List[ExtractedFact]