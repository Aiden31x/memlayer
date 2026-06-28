from fastapi import APIRouter,HTTPException

router=APIRouter(
    prefix="/memories",
    tags=["memories"]
)

router.get('/')
def get_memories():
    return {
        "message":"Not implemented yet"
    }