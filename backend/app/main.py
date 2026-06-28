from backend.app.routers import memories
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