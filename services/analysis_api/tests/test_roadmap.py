"""Roadmap ordering + AI plan validator tests (docs/07 stage 10)."""

import pytest

from app.core.config import settings
from app.pipeline import roadmap as roadmap_module
from app.pipeline.roadmap import _validate_plan, build_roadmap
from app.schemas.report import CourseRec, GapItem


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")


def _gap(
    skill_id: str,
    *,
    priority: str = "P0",
    importance: float = 1.0,
    target: int = 3,
    current: int = 0,
    adjacent: tuple[str, ...] = (),
) -> GapItem:
    return GapItem(
        skill_id=skill_id,
        priority=priority,
        importance=importance,
        target_level=target,
        current_level=current,
        adjacent_to=list(adjacent),
    )


def test_empty_gaps_yield_no_phases():
    assert build_roadmap([]) == []


def test_p2_only_gaps_yield_no_phases():
    assert build_roadmap([_gap("git", priority="P2")]) == []


def test_adjacent_fast_win_comes_first_within_p0():
    gaps = [_gap("jest"), _gap("typescript", adjacent=("javascript",))]
    phases = build_roadmap(gaps, hours_per_week=8)
    assert phases[0].focus_skills[0] == "typescript"


def test_p2_excluded_from_focus():
    gaps = [_gap("typescript"), _gap("git", priority="P2")]
    focus = [s for p in build_roadmap(gaps) for s in p.focus_skills]
    assert "typescript" in focus
    assert "git" not in focus


def test_capacity_packs_across_phases_in_order():
    gaps = [_gap(f"s{i}") for i in range(8)]
    phases = build_roadmap(gaps, hours_per_week=8)
    assert 2 <= len(phases) <= 3
    assert [s for p in phases for s in p.focus_skills] == [f"s{i}" for i in range(8)]


def test_resources_come_from_courses_covering_focus():
    courses = [CourseRec(course_id="c001", skills_covered=["typescript"])]
    phases = build_roadmap([_gap("typescript")], courses=courses)
    assert phases[0].resources == ["c001"]


def test_vietnamese_milestones():
    phases = build_roadmap([_gap("typescript")], language="vi")
    assert any("dự án" in m for m in phases[0].milestones)


def test_validator_rejects_unknown_focus():
    data = {
        "phases": [
            {
                "phase": "x",
                "duration": "4 weeks",
                "focus_skills": ["madeup"],
                "milestones": [],
                "resources": [],
            }
        ]
    }
    assert _validate_plan(data, gap_ids={"typescript"}, course_ids=set(), language="en") is None


def test_validator_remaps_labels_and_keeps_valid_fields():
    data = {
        "phases": [
            {
                "phase": "days 0-30",
                "duration": "",
                "focus_skills": ["typescript", "madeup"],
                "milestones": ["m1"],
                "resources": ["c1", "bad"],
            }
        ]
    }
    plan = _validate_plan(data, gap_ids={"typescript"}, course_ids={"c1"}, language="en")
    assert plan is not None
    assert plan[0].phase == "0-30 days"
    assert plan[0].duration == "4 weeks"
    assert plan[0].focus_skills == ["typescript"]
    assert plan[0].resources == ["c1"]


def test_validator_fills_missing_milestones_from_rules():
    data = {
        "phases": [
            {"phase": "", "duration": "2 weeks", "focus_skills": ["typescript"], "milestones": []}
        ]
    }
    plan = _validate_plan(data, gap_ids={"typescript"}, course_ids=set(), language="en")
    assert plan is not None
    assert plan[0].duration == "2 weeks"
    assert plan[0].milestones


def test_ai_plan_used_when_valid(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        roadmap_module.gemini,
        "generate_json",
        lambda *a, **k: {
            "phases": [
                {
                    "phase": "",
                    "duration": "1 week",
                    "focus_skills": ["typescript"],
                    "milestones": ["ai milestone"],
                    "resources": [],
                }
            ]
        },
    )
    phases = build_roadmap([_gap("typescript")])
    assert phases[0].phase == "0-30 days"
    assert phases[0].milestones == ["ai milestone"]


def test_ai_plan_garbage_falls_back_to_rules(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(roadmap_module.gemini, "generate_json", lambda *a, **k: {"phases": []})
    phases = build_roadmap([_gap("typescript")])
    assert phases
    assert phases[0].phase == "0-30 days"
    assert phases[0].milestones
