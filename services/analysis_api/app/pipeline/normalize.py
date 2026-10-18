"""Stage 4 — normalize raw skill mentions to taxonomy skill ids."""

import re

from app.data_loader import find_skills, skill_map
from app.schemas.cv import SkillItem

VIETNAMESE_MARKERS = re.compile(
    "[ăâđêôơưàảãạáằẳẵặắầẩẫậấèẻẽẹéềểễệếìỉĩịíòỏõọóồổỗộốờởỡợớùủũụúừửữựứỳỷỹỵý]",
    re.IGNORECASE,
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
            sid = _exact(raw)
        if sid and sid not in seen:
            seen.add(sid)
            out.append(SkillItem(raw=raw, skill_id=sid, level=3, evidence_span=raw))
    return out


def canonical(skill_id: str) -> str:
    entry = skill_map().get(skill_id)
    return entry["canonical_name"] if entry else skill_id


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
