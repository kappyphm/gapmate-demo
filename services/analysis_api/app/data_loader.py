"""Loads canonical data (taxonomy) and builds lookup indexes."""

import json
import re
from functools import lru_cache
from pathlib import Path

from app.core.config import settings


@lru_cache(maxsize=1)
def load_taxonomy() -> dict:
    path = Path(settings.data_dir) / "skills-taxonomy.json"
    if not path.exists():
        return {"skills": []}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def skill_map() -> dict[str, dict]:
    """skill_id -> skill entry."""
    return {s["skill_id"]: s for s in load_taxonomy().get("skills", [])}


@lru_cache(maxsize=1)
def term_index() -> list[tuple[re.Pattern, str]]:
    """Ordered list of (compiled pattern, skill_id). Longest terms first."""
    entries: list[tuple[str, str]] = []
    for s in load_taxonomy().get("skills", []):
        sid = s["skill_id"]
        terms = {s["canonical_name"], sid, sid.replace("_", " ")}
        for lang_terms in s.get("aliases", {}).values():
            terms.update(lang_terms)
        for t in terms:
            t = t.strip()
            if t:
                entries.append((t, sid))

    # longest first so "rest api" wins over "api"
    entries.sort(key=lambda e: len(e[0]), reverse=True)

    seen: set[str] = set()
    index: list[tuple[re.Pattern, str]] = []
    for term, sid in entries:
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        index.append((_compile(term), sid))
    return index


def _compile(term: str) -> re.Pattern:
    escaped = re.escape(term)
    if re.fullmatch(r"[A-Za-z0-9]+", term):
        return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def find_skills(text: str) -> list[tuple[str, str, str]]:
    """Return (skill_id, canonical_name, matched_term) found in text, de-duplicated."""
    found: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for pattern, sid in term_index():
        if sid in seen:
            continue
        m = pattern.search(text)
        if m:
            seen.add(sid)
            found.append((sid, skill_map()[sid]["canonical_name"], m.group(0)))
    return found
