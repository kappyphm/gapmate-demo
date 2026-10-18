"""JD parsing tests — LLM skill-id normalization (docs/04, docs/07)."""

from app.pipeline.parse_jd import _normalize_requirements
from app.schemas.jd import Requirement


def test_compound_llm_skill_id_is_split():
    reqs = [
        Requirement(
            raw="Nắm chắc JavaScript và React.", skill_id="javascript_react", required=True
        ),
        Requirement(
            raw="Biết HTML, CSS và Tailwind CSS.", skill_id="html_css_tailwind", required=True
        ),
    ]
    out = _normalize_requirements(reqs)
    ids = [r.skill_id for r in out]
    assert "javascript" in ids and "react" in ids
    assert "html" in ids and "css" in ids and "tailwindcss" in ids
    assert all(r.required for r in out)


def test_valid_skill_id_is_kept():
    reqs = [Requirement(raw="Python", skill_id="python", required=True)]
    out = _normalize_requirements(reqs)
    assert [r.skill_id for r in out] == ["python"]


def test_unknown_skill_id_without_known_terms_becomes_none():
    reqs = [
        Requirement(raw="Lorem ipsum dolor sit amet", skill_id="something_weird", required=False)
    ]
    out = _normalize_requirements(reqs)
    assert [r.skill_id for r in out] == [None]
    assert out[0].required is False
