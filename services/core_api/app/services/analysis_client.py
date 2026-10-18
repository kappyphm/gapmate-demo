"""HTTP client for the internal analysis-api (no persistence here yet — P4 adds history)."""

import httpx
from fastapi import HTTPException

from app.core.config import settings


async def analyze(cv_text: str, jd_text: str, options: dict, cv_layout: dict | None = None) -> dict:
    url = f"{settings.analysis_api_url}/v1/analyze"
    payload = {
        "cv_text": cv_text,
        "jd_text": jd_text,
        "cv_layout": cv_layout or {},
        "options": options,
    }
    headers = {"x-internal-key": settings.internal_api_key}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"analysis-api unreachable: {exc}") from exc
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"analysis-api error: {resp.text}")
    return resp.json()
