"""Course recommendation tests (docs/07 stage 11)."""

import pytest

from app.core.config import settings
from app.pipeline import recommend as recommend_module
from app.pipeline.recommend import recommend_courses
from app.schemas.report import GapItem


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")


def _gap(skill_id: str, *, priority: str = "P0", importance: float = 1.0, target: int = 3):
    return GapItem(skill_id=skill_id, priority=priority, importance=importance, target_level=target)


def test_no_gaps_no_courses():
    assert recommend_courses([]) == []


def test_uncovered_gap_yields_no_courses():
    assert recommend_courses([_gap("sveltekit")]) == []


def test_course_covers_gap_with_reason():
    recs = recommend_courses([_gap("typescript")], language="en")
    assert recs
    first = next(r for r in recs if r.course_id == "c001")
    assert "TypeScript" in first.match_reason
    assert "P0" in first.match_reason
    assert first.url
    assert first.duration.endswith("h")


def test_limit_respected():
    gaps = [_gap("typescript"), _gap("react"), _gap("javascript")]
    assert len(recommend_courses(gaps, limit=2)) <= 2


def test_ranking_prefers_level_and_language_fit(monkeypatch):
    catalog = [
        {
            "course_id": "adv",
            "title": "Advanced",
            "skills_covered": ["typescript"],
            "level": "advanced",
            "language": "en",
            "rating": 5.0,
            "duration_hours": 10,
        },
        {
            "course_id": "inter",
            "title": "Intermediate",
            "skills_covered": ["typescript"],
            "level": "intermediate",
            "language": "en",
            "rating": 4.0,
            "duration_hours": 10,
        },
    ]
    monkeypatch.setattr(recommend_module, "load_courses", lambda: catalog)
    recs = recommend_courses([_gap("typescript", target=3)])
    assert [r.course_id for r in recs] == ["inter", "adv"]


def test_ai_rerank_reorders_and_is_validated(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        recommend_module.gemini, "generate_json", lambda *a, **k: {"course_ids": ["c002", "c001"]}
    )
    recs = recommend_courses([_gap("typescript"), _gap("react")])
    assert recs[0].course_id == "c002"


def test_ai_rerank_garbage_keeps_deterministic_order(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        recommend_module.gemini, "generate_json", lambda *a, **k: {"course_ids": ["madeup"]}
    )
    recs = recommend_courses([_gap("typescript"), _gap("react")])
    assert [r.course_id for r in recs][0] != "madeup"
    assert all(r.course_id != "madeup" for r in recs)
