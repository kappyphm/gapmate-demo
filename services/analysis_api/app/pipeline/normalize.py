"""Stage 4 — normalize raw skill mentions to taxonomy skill ids."""

import re

from app.data_loader import compact_index, find_skills, skill_map, term_index
from app.schemas.cv import SkillItem

VIETNAMESE_MARKERS = re.compile(
    "[ăâđêôơưàảãạáằẳẵặắầẩẫậấèẻẽẹéềểễệếìỉĩịíòỏõọóồổỗộốờởỡợớùủũụúừửữựứỳỷỹỵý]",
    re.IGNORECASE,
)

_ACRONYM_RE = re.compile(r"^[A-Z][A-Z0-9]{1,6}$")
_CAMEL_RE = re.compile(r"^[A-Za-z][a-z0-9]+[A-Z][A-Za-z0-9]*$")
_VERSIONED_RE = re.compile(r"^[a-z]{1,10}[0-9]{1,2}[a-z]?$", re.IGNORECASE)
_DOTTED_RE = re.compile(r"^[a-z][a-z0-9]*(?:[.\-/][a-z0-9]+)+$")
_SPECIAL_RE = re.compile(r"^[a-z][a-z0-9]{0,4}[#+]+$")

_CANDIDATE_STOP = frozenset(
    {
        "ability",
        "able",
        "benefit",
        "benefits",
        "cv",
        "degree",
        "english",
        "experience",
        "experienced",
        "great",
        "jd",
        "knowledge",
        "must",
        "nice",
        "office",
        "plus",
        "problem",
        "require",
        "required",
        "requirements",
        "responsibilities",
        "salary",
        "solving",
        "strong",
        "team",
        "understanding",
        "work",
        "working",
        "year",
        "years",
    }
)


def detect_language(text: str) -> str:
    return "vi" if VIETNAMESE_MARKERS.search(text) else "en"


def skills_from_text(text: str) -> list[SkillItem]:
    """Detect taxonomy skills mentioned anywhere in text."""
    return [
        SkillItem(raw=term, skill_id=sid, level=3, evidence_span=_snippet(text, term))
        for sid, _canonical, term in find_skills(text)
    ]


def normalize_terms(raw_terms: list[str]) -> list[SkillItem]:
    """Map explicit raw skill strings (e.g. from the CV skills section) to skill ids."""
    out: list[SkillItem] = []
    seen: set[str] = set()
    for raw in raw_terms:
        raw = raw.strip()
        if not raw:
            continue
        matches = find_skills(raw)
        if matches:
            sid = matches[0][0]
        else:
            sid = _exact(raw) or discover_candidate(raw)
        if sid and sid not in seen:
            seen.add(sid)
            out.append(SkillItem(raw=raw, skill_id=sid, level=3, evidence_span=raw))
    return out


def canonical(skill_id: str) -> str:
    entry = skill_map().get(skill_id)
    return entry["canonical_name"] if entry else skill_id


_TECH_TLDS = frozenset({"js", "ts", "net", "io", "css", "html"})


def discover_candidate(raw: str) -> str | None:
    """Map an out-of-taxonomy skill-like phrase to a stable id (docs/07 stage 4).

    Conservative: only acronyms, camelCase, versioned and tech-suffixed tokens become
    new candidates; known compact forms resolve back to the taxonomy; everything else
    is dropped.
    """
    term = raw.strip()
    if not 2 <= len(term) <= 30:
        return None
    low = term.lower()
    parts = [p for p in re.split(r"[\s,;/+.]+", low) if p]
    if any(part in _CANDIDATE_STOP for part in parts):
        return None
    compact = re.sub(r"[^a-z0-9]", "", low)
    if len(compact) < 2:
        return None
    hit = compact_index().get(compact)
    if hit:
        return hit
    if len(parts) > 1 and all(
        compact_index().get(re.sub(r"[^a-z0-9]", "", part)) for part in parts
    ):
        # Every part already resolves to a taxonomy skill (e.g. "HTML/CSS").
        return None
    if _DOTTED_RE.match(low) and low.rsplit(".", 1)[-1] not in _TECH_TLDS:
        return None
    if not (
        _ACRONYM_RE.match(term)
        or _CAMEL_RE.match(term)
        or _VERSIONED_RE.match(low)
        or _DOTTED_RE.match(low)
        or _SPECIAL_RE.match(low)
    ):
        return None
    prefix = re.sub(r"[0-9]+$", "", compact)
    if prefix != compact and len(prefix) >= 2:
        return compact_index().get(prefix) or compact
    return compact


def discover_candidates_in(text: str, *, exclude: set[str] | None = None) -> list[tuple[str, str]]:
    """Scan free text for candidate tokens; returns [(raw, skill_id)] de-duplicated.

    Tokens that fall inside a longer taxonomy match (e.g. "API" in "REST API") are
    skipped so one phrase does not produce two competing requirement ids.
    """
    excluded = exclude or set()
    spans = [
        m.span()
        for pattern, _sid in term_index()
        for m in pattern.finditer(text)
        if len(m.group(0).strip()) > 0
    ]
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for match in re.finditer(r"[A-Za-z][A-Za-z0-9.#+/\-]{1,20}", text):
        start = match.start()
        end = start + len(match.group(0).rstrip(".-/"))
        if any(cs <= start and end <= ce and (ce - cs) > (end - start) for cs, ce in spans):
            continue
        raw = match.group(0).strip(".-/")
        sid = discover_candidate(raw)
        if sid and sid not in seen and sid not in excluded:
            seen.add(sid)
            out.append((raw, sid))
    return out


def _exact(raw: str) -> str | None:
    key = raw.lower().strip()
    for s in skill_map().values():
        terms = {
            s["canonical_name"].lower(),
            s["skill_id"].lower(),
            s["skill_id"].replace("_", " "),
        }
        for lang_terms in s.get("aliases", {}).values():
            terms.update(t.lower() for t in lang_terms)
        if key in terms:
            return s["skill_id"]
    return None


def _snippet(text: str, term: str, width: int = 60) -> str:
    idx = text.lower().find(term.lower())
    if idx < 0:
        return term
    start = max(0, idx - width // 2)
    return text[start : idx + len(term) + width // 2].replace("\n", " ").strip()
