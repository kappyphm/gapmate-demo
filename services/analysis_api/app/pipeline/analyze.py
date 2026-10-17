"""Pipeline orchestrator: extract → parse → normalize → match → score (P1)."""

from datetime import datetime, timezone

from app.core.config import settings
from app.pipeline.match import match
from app.pipeline.parse_cv import cv_seniority, parse_cv
from app.pipeline.parse_jd import parse_jd
from app.pipeline.score import score
from app.schemas.report import AnalyzeRequest, Report, ReportMeta


def run_analysis(req: AnalyzeRequest) -> Report:
    cv = parse_cv(req.cv_text)
    jd = parse_jd(req.jd_text)
    matched, missing = match(jd, cv)
    mode = "gemini" if cv.meta.parse_confidence >= 0.8 else "heuristic"
    result = score(
        cv,
        jd,
        matched,
        missing,
        cv_seniority=cv_seniority(req.cv_text),
        mode=mode,
        parse_confidence=cv.meta.parse_confidence,
    )
    confidence = round(min(0.95, (cv.meta.parse_confidence + 0.7) / 2), 2)
    return Report(
        meta=ReportMeta(
            pipeline_version=settings.pipeline_version,
            created_at=datetime.now(timezone.utc).isoformat(),
            confidence=confidence,
            mode=mode,
            role_template=req.options.role_template,
        ),
        match=result,
    )
