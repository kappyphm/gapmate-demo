"""Match cascade tests: no fabricated matches, consistent with ATS coverage (docs/04 Part A)."""

import pytest

from app.core.config import settings
from app.pipeline.ats import run_ats
from app.pipeline.match import match
from app.pipeline.normalize import canonical
from app.schemas.cv import Contact, CVDoc, SkillItem
from app.schemas.jd import JDDoc, Requirement


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")


def _cv() -> CVDoc:
    return CVDoc(
        contact=Contact(email="a@b.com", phone="0900"),
        skills=[SkillItem(raw="CSS", skill_id="css")],
    )


def test_related_skill_is_not_matched():
    """Having CSS does not mean the candidate knows Tailwind."""
    jd = JDDoc(
        requirements=[Requirement(raw="Tailwind CSS", skill_id="tailwindcss", required=True)]
    )
    matched, missing = match(jd, _cv())
    assert matched == []
    assert [m.skill_id for m in missing] == ["tailwindcss"]


def test_missing_includes_nice_to_have():
    jd = JDDoc(
        requirements=[
            Requirement(raw="CSS", skill_id="css", required=True),
            Requirement(raw="Figma", skill_id="figma", required=False, importance=0.5),
        ]
    )
    matched, missing = match(jd, _cv())
    assert [m.skill_id for m in matched] == ["css"]
    assert [m.skill_id for m in missing] == ["figma"]
    assert missing[0].required is False


def test_semantic_band_defers_to_llm(monkeypatch):
    from app.pipeline import match as m

    monkeypatch.setattr(m, "embed", lambda text: [1.0, 0.0])
    monkeypatch.setattr(m, "cosine", lambda a, b: 0.90)
    seen: list[str] = []
    monkeypatch.setattr(m, "_llm_adjudicate", lambda req, skill: seen.append(req.skill_id) or None)

    jd = JDDoc(requirements=[Requirement(raw="TypeScript", skill_id="typescript", required=True)])
    matched, missing = match(jd, _cv())
    assert seen == ["typescript"]
    assert matched == []
    assert [x.skill_id for x in missing] == ["typescript"]


def test_semantic_above_threshold_is_accepted(monkeypatch):
    from app.pipeline import match as m

    monkeypatch.setattr(m, "embed", lambda text: [1.0, 0.0])
    monkeypatch.setattr(m, "cosine", lambda a, b: 0.99)

    jd = JDDoc(requirements=[Requirement(raw="TypeScript", skill_id="typescript", required=True)])
    matched, missing = match(jd, _cv())
    assert matched and matched[0].match_type == "semantic"
    assert missing == []


def test_matched_is_subset_of_jd_requirements_and_coverage():
    jd = JDDoc(requirements=[Requirement(raw="CSS", skill_id="css", required=True, level=3)])
    cv = _cv()
    matched, _ = match(jd, cv)
    matched_ids = {m.skill_id for m in matched}

    ats = run_ats(cv, jd, text="- CSS", layout={}, matched_ids=matched_ids)
    covered = set(ats.keyword_coverage.matched)
    for skill_id in matched_ids:
        assert canonical(skill_id) in covered
