"""Full analysis endpoint (implemented in P1+)."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/analyze")
async def analyze() -> dict:
    raise HTTPException(status_code=501, detail="Analysis pipeline lands in P1")
