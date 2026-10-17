"""Course recommendation endpoint + catalog access (P3)."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core.config import settings

router = APIRouter()


def _load_catalog() -> list[dict]:
    path = Path(settings.data_dir) / "courses.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("courses", [])


@router.get("/courses")
async def list_courses() -> dict:
    return {"courses": _load_catalog()}


@router.post("/recommend-courses")
async def recommend_courses() -> dict:
    raise HTTPException(status_code=501, detail="Recommender lands in P3")
