from typing import Optional,List,Literal
from pydantic import BaseModel,Field

class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str


class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str

class ConversationRequest(BaseModel):
    messages: List[Message]

class ExtractedFact(BaseException):
    category: str
    key:str
    value:str
    confidence:float
    evidence:str

class ExtractionResponse(BaseModel):
    facts: List[ExtractedFact]