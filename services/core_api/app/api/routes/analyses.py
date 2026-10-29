"""Analysis orchestration + history endpoints (history persistence lands in P4)."""

import logging
import time
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.schemas.analysis import AnalyzeRequest
from app.services import analysis_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("")
async def create_analysis(payload: AnalyzeRequest) -> dict:
    started = time.perf_counter()
    logger.info(
        "analysis_request_received cv_chars=%d jd_chars=%d",
        len(payload.cv_text),
        len(payload.jd_text),
    )
    report = await analysis_client.analyze(
        payload.cv_text, payload.jd_text, payload.options.model_dump(), payload.cv_layout
    )
    duration_ms = round((time.perf_counter() - started) * 1000)
    usage = (report.get("meta") or {}).get("usage") or {}
    logger.info(
        "analysis_request_completed duration_ms=%d total_tokens=%s llm_calls=%s",
        duration_ms,
        usage.get("total_tokens", "-"),
        usage.get("llm_calls", "-"),
    )
    return report


@router.post("/extract")
async def extract_document(file: Annotated[UploadFile, File()]) -> dict:
    """Extract text (+ CV layout facts) from an uploaded PDF/DOCX/TXT/MD file.

    The web uses this to turn a user's real CV/JD file into the text the
    analysis pipeline consumes; nothing is stored (P4 adds history).
    """
    data = await file.read()
    logger.info(
        "extract_request filename=%s bytes=%d",
        file.filename or "",
        len(data),
    )
    return await analysis_client.extract(file.filename or "", data, file.content_type)


@router.get("")
async def list_analyses() -> dict:
    return {"analyses": [], "note": "history persistence lands in P4"}
