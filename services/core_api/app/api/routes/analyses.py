"""Analysis orchestration + history endpoints (P1 orchestrator, P4 persistence)."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("")
async def create_analysis() -> dict:
    raise HTTPException(status_code=501, detail="Analysis orchestration lands in P4")


@router.get("")
async def list_analyses() -> dict:
    raise HTTPException(status_code=501, detail="History lands in P4")
