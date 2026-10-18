"""ATS rules engine tests (docs/04 Part C)."""

from app.pipeline.ats import SEVERITY_WEIGHT, _bullets, run_ats
from app.schemas.cv import Contact, CVDoc, ExperienceItem, SkillItem
from app.schemas.jd import JDDoc, Requirement

TEXT = """## Summary
Frontend developer.

## Experience
- Built the checkout page with React.
- Improved load time by 40%.

## Education
Bachelor of IT.

## Skills
JavaScript, React
"""


def _cv() -> CVDoc:
    return CVDoc(
        contact=Contact(email="a@example.com", phone="0900000001"),
        skills=[
            SkillItem(raw="React", skill_id="react", level=3),
            SkillItem(raw="JavaScript", skill_id="javascript", level=4),
        ],
        experience=[ExperienceItem(title="Frontend Developer", bullets=["Built checkout page."])],
    )


def _jd() -> JDDoc:
    return JDDoc(
        requirements=[
            Requirement(raw="React", skill_id="react", required=True, level=3),
            Requirement(raw="TypeScript", skill_id="typescript", required=True, level=4),
        ],
        keywords=["typescript"],
    )


def test_score_in_range_and_weights():
    ats = run_ats(_cv(), _jd(), text=TEXT, layout={"file_type": "txt"})
    assert 0 <= ats.score <= 100
    for issue in ats.issues:
        assert issue.weight == SEVERITY_WEIGHT[issue.severity]


def test_keyword_coverage_matched_and_missing():
    ats = run_ats(_cv(), _jd(), text=TEXT, layout={})
    assert "React" in ats.keyword_coverage.matched
    assert "TypeScript" in ats.keyword_coverage.missing


def test_multi_column_flags_A3():
    ats = run_ats(_cv(), _jd(), text=TEXT, layout={"single_column": False})
    issue = next(i for i in ats.issues if i.code == "A3")
    assert issue.passed is False
    assert "A3" in ats.format_issues


def test_missing_contact_fails_A6_and_B3():
    cv = _cv()
    cv.contact = Contact()
    ats = run_ats(cv, _jd(), text=TEXT, layout={})
    assert next(i for i in ats.issues if i.code == "A6").passed is False
    assert next(i for i in ats.issues if i.code == "B3").passed is False


def test_issue_serializes_pass_alias():
    ats = run_ats(_cv(), _jd(), text=TEXT, layout={})
    payload = ats.issues[0].model_dump(by_alias=True)
    assert "pass" in payload


def test_bullet_fallback_uses_full_line():
    cv = _cv()
    cv.experience = []
    text = "## Experience\n- Built the checkout page with React.\n"
    assert _bullets(cv, text) == ["Built the checkout page with React."]


def test_b2_accepts_role_month_year_with_education_years():
    text = "## Experience\n### Acme — Dev (06/2024 – nay)\n" "## Education\n- Uni (2019 – 2023)\n"
    ats = run_ats(_cv(), _jd(), text=text, layout={})
    assert next(i for i in ats.issues if i.code == "B2").passed is True


def test_c5_passes_when_no_acronyms_present():
    ats = run_ats(_cv(), _jd(), text=TEXT, layout={})
    assert next(i for i in ats.issues if i.code == "C5").passed is True


def test_matched_ids_feed_keyword_coverage():
    ats = run_ats(_cv(), _jd(), text=TEXT, layout={}, matched_ids={"typescript"})
    assert "TypeScript" in ats.keyword_coverage.matched
    assert "TypeScript" not in ats.keyword_coverage.missing
