"""Pipeline orchestrator: extract → parse → normalize → match → score → ats → suggest (P2)."""

from datetime import UTC, datetime

from app.core.config import settings
from app.pipeline.ats import run_ats
from app.pipeline.match import match
from app.pipeline.parse_cv import cv_seniority, parse_cv
from app.pipeline.parse_jd import parse_jd
from app.pipeline.score import score
from app.pipeline.suggest import build_suggestions, project_ats
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

    matched_ids = {m.skill_id for m in matched if m.skill_id}
    ats = run_ats(cv, jd, text=req.cv_text, layout=req.cv_layout, matched_ids=matched_ids)
    suggestions = build_suggestions(cv, ats, text=req.cv_text)
    preview = project_ats(
        cv,
        jd,
        text=req.cv_text,
        layout=req.cv_layout,
        suggestions=suggestions,
        before=ats.score,
        matched_ids=matched_ids,
    )
    ats.projected_score = preview.after

    confidence = round(min(0.95, (cv.meta.parse_confidence + 0.7) / 2), 2)
    return Report(
        meta=ReportMeta(
            pipeline_version=settings.pipeline_version,
            created_at=datetime.now(UTC).isoformat(),
            confidence=confidence,
            mode=mode,
            role_template=req.options.role_template,
        ),
        match=result,
        ats=ats,
        suggestions=suggestions,
        ats_preview=preview,
    )
