"""Suggestion generation + before/after ATS projection tests (docs/04 Part E)."""

from app.pipeline.ats import run_ats
from app.pipeline.suggest import build_suggestions, project_ats
from app.schemas.cv import Contact, CVDoc, ExperienceItem, SkillItem
from app.schemas.jd import JDDoc, Requirement

CV_TEXT = "## Skills\nJavaScript\n\n## Experience\n- Worked on the website.\n"


def _cv() -> CVDoc:
    return CVDoc(
        contact=Contact(email="a@b.com", phone="0900"),
        skills=[SkillItem(raw="JS", skill_id="javascript")],
    )


def _jd() -> JDDoc:
    return JDDoc(
        requirements=[
            Requirement(raw="JavaScript", skill_id="javascript", required=True),
            Requirement(raw="TypeScript", skill_id="typescript", required=True),
        ],
        keywords=["typescript"],
    )


def test_projection_improves_or_keeps_score():
    ats = run_ats(_cv(), _jd(), text=CV_TEXT, layout={})
    suggestions = build_suggestions(_cv(), ats, text=CV_TEXT)
    preview = project_ats(
        _cv(), _jd(), text=CV_TEXT, layout={}, suggestions=suggestions, before=ats.score
    )
    assert preview.after >= preview.before


def test_no_new_skills_are_suggested():
    """Missing JD skills are a gap (P3), never an automatic CV edit here."""
    ats = run_ats(_cv(), _jd(), text=CV_TEXT, layout={})
    suggestions = build_suggestions(_cv(), ats, text=CV_TEXT)
    assert not any(s.code == "C1" for s in suggestions)
    assert all(not s.jd_keywords_addressed for s in suggestions)


def test_fallback_bullet_uses_full_line():
    text = (
        "## Skills\nJavaScript\n\n" "## Experience\n- Worked on the internal website for clients.\n"
    )
    cv = _cv()
    ats = run_ats(cv, _jd(), text=text, layout={})
    suggestions = build_suggestions(cv, ats, text=text)
    originals = [s.original for s in suggestions if s.code in ("C3", "C4")]
    assert originals
    assert all(o.startswith("Worked on the internal") for o in originals)


def test_vietnamese_bullet_is_not_prefixed_with_english():
    text = "## Kỹ năng\nJavaScript\n\n## Kinh nghiệm\n- Tham gia xây dựng giao diện.\n"
    cv = CVDoc(
        contact=Contact(email="a@b.com", phone="0900"),
        skills=[SkillItem(raw="JS", skill_id="javascript")],
        experience=[ExperienceItem(title="Dev", bullets=["Tham gia xây dựng giao diện."])],
    )
    ats = run_ats(cv, _jd(), text=text, layout={})
    suggestions = build_suggestions(cv, ats, text=text)
    c3 = [s for s in suggestions if s.code == "C3"]
    assert c3
    assert c3[0].improved.startswith("Đã ")
    assert "Delivered" not in c3[0].improved


def test_vietnamese_suggestions_are_localized():
    text = "## Kỹ năng\nJavaScript\n\n## Kinh nghiệm\n- Tham gia xây dựng giao diện.\n"
    cv = CVDoc(
        contact=Contact(email="a@b.com", phone="0900"),
        skills=[SkillItem(raw="JS", skill_id="javascript")],
        experience=[ExperienceItem(title="Dev", bullets=["Tham gia xây dựng giao diện."])],
    )
    ats = run_ats(cv, _jd(), text=text, layout={})
    suggestions = build_suggestions(cv, ats, text=text)
    c4 = next(s for s in suggestions if s.code == "C4")
    assert "bổ sung số liệu" in c4.improved
    assert "số liệu" in c4.reason
