"""Candidate discovery tests (docs/07 stage 4)."""

from app.pipeline.normalize import (
    discover_candidate,
    discover_candidates_in,
    normalize_terms,
)


def test_known_acronym_resolves_to_taxonomy():
    assert discover_candidate("AWS") == "aws"


def test_new_acronym_becomes_candidate():
    assert discover_candidate("BUN") == "bun"
    assert discover_candidate("SolidJS") == "solidjs"


def test_compact_form_resolves_to_taxonomy():
    assert discover_candidate("React-Native") == "reactnative"
    assert discover_candidate("Next.js") == "nextjs"


def test_versioned_token_resolves_prefix():
    assert discover_candidate("vue3") == "vue"
    assert discover_candidate("es6") is not None


def test_generic_words_are_rejected():
    assert discover_candidate("management") is None
    assert discover_candidate("team work") is None
    assert discover_candidate("JD") is None
    assert discover_candidate("experience") is None


def test_domain_like_token_rejected():
    assert discover_candidate("example.com") is None


def test_multiword_of_known_parts_rejected_as_covered():
    assert discover_candidate("HTML/CSS") is None


def test_normalize_terms_assigns_candidate_ids():
    items = normalize_terms(["SolidJS"])
    assert items
    assert items[0].skill_id == "solidjs"


def test_free_text_scan_skips_tokens_inside_longer_taxonomy_match():
    text = "Hiểu biết về gọi REST API."
    raws = [raw for raw, _sid in discover_candidates_in(text)]
    assert "API" not in raws


def test_free_text_scan_finds_new_acronym():
    raws = dict(discover_candidates_in("Kinh nghiệm với SOLIDJS là một lợi thế."))
    assert raws.get("SOLIDJS") == "solidjs"
