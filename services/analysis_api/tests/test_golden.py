"""Golden-set regression: the sample CV/JD stays within expected score ranges.

Gemini is disabled so the run is deterministic (docs/07 §7).
"""

from pathlib import Path

import pytest

from app.core.config import settings
from app.pipeline.analyze import run_analysis
from app.pipeline.normalize import canonical
from app.schemas.report import AnalyzeRequest


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")


def _samples() -> tuple[str, str]:
    base = Path(settings.data_dir) / "samples"
    cv = (base / "cv_vi.md").read_text(encoding="utf-8")
    jd = (base / "jd_frontend.md").read_text(encoding="utf-8")
    return cv, jd


def test_golden_ranges():
    cv_text, jd_text = _samples()
    report = run_analysis(AnalyzeRequest(cv_text=cv_text, jd_text=jd_text))

    assert report.meta.mode == "heuristic"
    assert 55 <= report.match.overall <= 90
    assert report.ats is not None
    assert 50 <= report.ats.score <= 100
    assert 0.0 < report.meta.confidence <= 0.95


def test_golden_projection_never_decreases():
    cv_text, jd_text = _samples()
    report = run_analysis(AnalyzeRequest(cv_text=cv_text, jd_text=jd_text))

    assert report.ats_preview is not None
    assert report.ats_preview.after >= report.ats_preview.before
    assert report.suggestions
    assert all(s.section for s in report.suggestions)


def test_golden_match_and_coverage_are_consistent():
    """A skill reported as matched must never also be reported as a missing keyword."""
    cv_text, jd_text = _samples()
    report = run_analysis(AnalyzeRequest(cv_text=cv_text, jd_text=jd_text))

    assert report.ats is not None
    missing = set(report.ats.keyword_coverage.missing)
    for item in report.match.matched:
        assert canonical(item.skill_id) not in missing
    for item in report.match.missing:
        assert canonical(item.skill_id) in missing


def test_golden_no_skills_are_invented_in_suggestions():
    cv_text, jd_text = _samples()
    report = run_analysis(AnalyzeRequest(cv_text=cv_text, jd_text=jd_text))
    assert all(not s.jd_keywords_addressed for s in report.suggestions)
