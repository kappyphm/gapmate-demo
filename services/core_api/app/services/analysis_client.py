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


async def extract(filename: str, data: bytes, content_type: str | None = None) -> dict:
    """Forward an uploaded document (PDF/DOCX/TXT/MD) to analysis-api /v1/extract.

    Returns ``{"text": ..., "layout": {...}}``. A 400 from analysis-api means
    the file itself was rejected (type/size/corrupt) and is passed through as
    a 400 so the user sees the real reason; transport failures become 502.
    """
    url = f"{settings.analysis_api_url}/v1/extract"
    headers = {"x-internal-key": settings.internal_api_key}
    files = {"file": (filename, data, content_type or "application/octet-stream")}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(url, files=files, headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"analysis-api unreachable: {exc}") from exc
    if resp.status_code == 400:
        try:
            detail = resp.json().get("detail", "File could not be extracted.")
        except ValueError:
            detail = "File could not be extracted."
        raise HTTPException(status_code=400, detail=detail)
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"analysis-api error: {resp.text}")
    return resp.json()
