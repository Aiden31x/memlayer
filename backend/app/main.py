from fastapi import FastAPI

from app.routers import memories
from app.db.qdrant_service import QdrantService
from app.core.config import settings

app = FastAPI(
    title="Memory API",
    version="1.0.0",
)

app.include_router(memories.router)


@app.get("/")
def root():
    return {"message": "Memory API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    app.state.vector_store = QdrantService()

    if not await app.state.vector_store.health_check():
        raise RuntimeError("Vector store is not healthy")

    await app.state.vector_store.ensure_collection(settings.qdrant_collection)
