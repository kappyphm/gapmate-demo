"""Standalone ATS check endpoint (P2)."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/ats-check")
async def ats_check() -> dict:
    raise HTTPException(status_code=501, detail="ATS rules engine lands in P2")
