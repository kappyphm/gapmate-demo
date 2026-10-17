"""Skill taxonomy access."""

import json
from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/taxonomy")
async def get_taxonomy() -> dict:
    path = Path(settings.data_dir) / "skills-taxonomy.json"
    if not path.exists():
        return {"skills": []}
    return json.loads(path.read_text(encoding="utf-8"))
