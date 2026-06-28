from fastapi import APIRouter
from app.models.schemas import ConversationRequest, ExtractionResponse
from app.services.extraction import ExtractionService

router = APIRouter(
    prefix="/memories",
    tags=["memories"]
)

extraction_service = ExtractionService()


@router.get("/")
def get_memories():
    return {"message": "Not implemented yet"}


@router.post("/", response_model=ExtractionResponse)
def create_memory(request: ConversationRequest):
    extracted = extraction_service.extract_facts(request)
    return extracted