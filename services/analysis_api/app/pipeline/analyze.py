"""Pipeline orchestrator: extract → parse → normalize → match → score → ats → suggest →
gap → recommend → roadmap (P3).

Each run is wrapped in LLM usage tracking (issue #4): one structured
``analysis_request`` log line per request, and the totals are attached to
``Report.meta.usage``.
"""

import logging
import time
from datetime import UTC, datetime

from app.core.config import settings
from app.llm import usage
from app.pipeline.ats import run_ats
from app.pipeline.gap import build_gaps
from app.pipeline.match import match
from app.pipeline.parse_cv import cv_seniority, parse_cv
from app.pipeline.parse_jd import parse_jd
from app.pipeline.recommend import recommend_courses
from app.pipeline.roadmap import build_roadmap
from app.pipeline.score import score
from app.pipeline.suggest import build_suggestions, project_ats
from app.schemas.report import AnalyzeRequest, Report, ReportMeta

logger = logging.getLogger(__name__)


def run_analysis(req: AnalyzeRequest) -> Report:
    tracker, token = usage.start_tracking()
    started = time.perf_counter()
    try:
        report = _run_pipeline(req)
    except Exception:
        usage.stop_tracking(token)
        raise
    duration_ms = round((time.perf_counter() - started) * 1000)
    totals = tracker.snapshot()
    usage.stop_tracking(token)

    report.meta.usage = totals
    logger.info(
        "analysis_request mode=%s duration_ms=%d cv_chars=%d jd_chars=%d "
        "llm_calls=%d prompt_tokens=%d output_tokens=%d total_tokens=%d "
        "embedding_calls=%d embedding_input_chars=%d overall=%d ats=%s",
        report.meta.mode,
        duration_ms,
        len(req.cv_text),
        len(req.jd_text),
        totals["llm_calls"],
        totals["prompt_tokens"],
        totals["output_tokens"],
        totals["total_tokens"],
        totals["embedding_calls"],
        totals["embedding_input_chars"],
        report.match.overall,
        report.ats.score if report.ats else "-",
    )
    return report


def _run_pipeline(req: AnalyzeRequest) -> Report:
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

    lang = cv.language if cv.language in {"vi", "en"} else "en"
    gaps = build_gaps(jd, matched, cv.skills, language=lang)
    courses = recommend_courses(gaps, language=lang)
    roadmap = build_roadmap(
        gaps, hours_per_week=req.options.hours_per_week, language=lang, courses=courses
    )

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
        gaps=gaps,
        roadmap=roadmap,
        courses=courses,
        suggestions=suggestions,
        ats_preview=preview,
    )
