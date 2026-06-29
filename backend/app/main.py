from app.routers import memories
from app.models.schemas import ConversationRequest
from fastapi import FastAPI

app=FastAPI(
    title="Memory API",
    version="1.0.0",
)

app.include_router(memories.router)

@app.get("/")
def root():
    return {
        "message": " Memory API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/extract")
async def extract_facts(request: ConversationRequest):
    extracted = await memories.extraction_service.extract_facts(request)
    return extracted
