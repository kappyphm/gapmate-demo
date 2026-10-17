"""User endpoints (P4)."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/me")
async def me() -> dict:
    raise HTTPException(status_code=501, detail="User profile lands in P4")
