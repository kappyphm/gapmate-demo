"""Analysis orchestration + history endpoints (history persistence lands in P4)."""

from fastapi import APIRouter

from app.schemas.analysis import AnalyzeRequest
from app.services import analysis_client

router = APIRouter()


@router.post("")
async def create_analysis(payload: AnalyzeRequest) -> dict:
    return await analysis_client.analyze(
        payload.cv_text, payload.jd_text, payload.options.model_dump(), payload.cv_layout
    )


@router.get("")
async def list_analyses() -> dict:
    return {"analyses": [], "note": "history persistence lands in P4"}
