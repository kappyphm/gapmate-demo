"""Auth endpoints — Google OAuth + JWT (implemented in P4)."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/google")
async def google_login() -> dict:
    raise HTTPException(status_code=501, detail="Google OAuth lands in P4")


@router.post("/refresh")
async def refresh() -> dict:
    raise HTTPException(status_code=501, detail="Token refresh lands in P4")
