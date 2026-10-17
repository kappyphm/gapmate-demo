"""Subscription & quota endpoints (P4)."""

from fastapi import APIRouter

router = APIRouter()

TIERS = {
    "free": {"quota_limit": 5, "price_usd": 0},
    "pro": {"quota_limit": 200, "price_usd": 19},
}


@router.get("")
async def list_plans() -> dict:
    return {"tiers": TIERS}
