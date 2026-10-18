"""Gap prioritization tests (docs/04 Part D)."""

from app.pipeline.gap import build_gaps
from app.schemas.cv import SkillItem
from app.schemas.jd import JDDoc, Requirement
from app.schemas.report import MatchedItem


def _cv_skills(*ids: str) -> list[SkillItem]:
    return [SkillItem(raw=sid, skill_id=sid) for sid in ids]


def _jd(skill_id: str, *, required: bool = True, importance: float = 1.0, level: int = 3):
    return JDDoc(
        requirements=[
            Requirement(
                raw=skill_id,
                skill_id=skill_id,
                required=required,
                importance=importance,
                level=level,
            )
        ]
    )


def test_missing_required_high_importance_is_p0():
    gaps = build_gaps(_jd("typescript"), [], _cv_skills("javascript"))
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.skill_id == "typescript"
    assert gap.priority == "P0"
    assert gap.current_level == 0
    assert gap.target_level == 3
    assert gap.importance == 1.0
    assert gap.reason


def test_missing_nice_to_have_is_p1():
    """Optional skills use the 0.6 factor, so the same importance lands a tier lower."""
    gaps = build_gaps(_jd("nextjs", required=False, importance=0.5), [], _cv_skills())
    assert gaps[0].priority == "P1"


def test_adjacent_fast_win_marked_from_taxonomy_related():
    gaps = build_gaps(_jd("typescript"), [], _cv_skills("javascript"))
    assert gaps[0].adjacent_to == ["javascript"]


def test_level_gap_reports_current_and_target():
    matched = [MatchedItem(skill_id="react", match_score=0.8, match_type="llm")]
    gaps = build_gaps(_jd("react", level=5), matched, _cv_skills("react"))
    assert gaps[0].current_level == 3
    assert gaps[0].target_level == 5
    assert "below" in gaps[0].reason


def test_fully_matched_skill_is_not_a_gap():
    matched = [MatchedItem(skill_id="react", match_score=1.0, match_type="exact")]
    assert build_gaps(_jd("react"), matched, _cv_skills("react")) == []


def test_high_partial_match_is_p2_already_strong():
    matched = [MatchedItem(skill_id="react", match_score=0.97, match_type="llm")]
    gaps = build_gaps(_jd("react"), matched, _cv_skills("react"))
    assert gaps[0].priority == "P2"


def test_gaps_sorted_by_priority():
    jd = JDDoc(
        requirements=[
            Requirement(raw="nice", skill_id="nextjs", required=False, importance=0.5),
            Requirement(raw="req", skill_id="typescript", required=True, importance=1.0),
        ]
    )
    gaps = build_gaps(jd, [], _cv_skills())
    assert [g.priority for g in gaps] == ["P0", "P1"]


def test_vietnamese_reason_localized():
    gaps = build_gaps(_jd("typescript"), [], _cv_skills(), language="vi")
    assert gaps[0].reason.startswith("JD yêu cầu")
