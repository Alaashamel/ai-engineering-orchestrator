from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-software-engineering-api", "version": "0.1.0"}
