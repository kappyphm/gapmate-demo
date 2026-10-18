"""Taxonomy integrity: every skill is addressable and unambiguous (docs/03)."""

from collections import defaultdict

from app.data_loader import load_taxonomy


def _skills() -> list[dict]:
    return load_taxonomy().get("skills", [])


def test_taxonomy_has_skills():
    skills = _skills()
    assert skills
    assert load_taxonomy().get("version")


def test_skill_ids_are_unique_and_named():
    skills = _skills()
    ids = [s["skill_id"] for s in skills]
    assert len(ids) == len(set(ids))
    for s in skills:
        assert s["skill_id"].strip()
        assert s["canonical_name"].strip()


def test_multi_industry_categories_present():
    categories = {s["category"] for s in _skills()}
    expected = {
        "marketing",
        "sales",
        "finance",
        "hr",
        "design",
        "data",
        "logistics",
        "pm",
    }
    assert expected <= categories


def test_terms_do_not_collide():
    """No term (id, canonical, alias) may point at two different skills."""
    owners: dict[str, set[str]] = defaultdict(set)
    for s in _skills():
        sid = s["skill_id"]
        terms = {s["canonical_name"], sid, sid.replace("_", " ")}
        for lang_terms in s.get("aliases", {}).values():
            terms.update(lang_terms)
        for term in terms:
            term = term.strip().lower()
            if term:
                owners[term].add(sid)

    conflicts = {term: sids for term, sids in owners.items() if len(sids) > 1}
    assert not conflicts, f"ambiguous terms: {conflicts}"
