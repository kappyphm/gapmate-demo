"""Full analysis endpoint."""

from fastapi import APIRouter

from app.pipeline.analyze import run_analysis
from app.schemas.report import AnalyzeRequest, Report

router = APIRouter()


@router.post("/analyze", response_model=Report)
async def analyze(payload: AnalyzeRequest) -> Report:
    return run_analysis(payload)
