"""Stage 3 — parse JD text into a structured JDDoc (Gemini, else heuristic)."""

import re

from app.data_loader import find_skills, skill_map
from app.llm import gemini
from app.pipeline.normalize import canonical, detect_language
from app.schemas.jd import JDDoc, Requirement

NICE_RE = re.compile(
    r"^#{0,3}\s*(nice to have|niv+|điểm cộng|ưu tiên|plus)\b.*$", re.IGNORECASE | re.MULTILINE
)
REQUIRED_RE = re.compile(
    r"^#{0,3}\s*(yêu cầu|requirements?|required|must have|bắt buộc)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)
YEARS_RE = re.compile(r"(\d+)\s*\+?\s*(năm|years|yrs)", re.IGNORECASE)

SENIORITY = {"senior": "senior", "middle": "mid", "mid-level": "mid", "junior": "junior"}

PROMPT = """You are an expert job-description parser. Extract structured requirements.
Rules:
- language: "vi" or "en".
- requirements: every skill/qualification; set required=true for must-have, false for nice-to-have.
- importance: 1.0 for must-have, 0.5 for nice-to-have.
- level: 1..5 proficiency implied by the JD (default 3).
- Do NOT invent anything not present.
Respond with a single JSON object.
JD:
---
{jd}
---"""


def parse_jd(text: str) -> JDDoc:
    doc = _parse_with_gemini(text) or _parse_heuristic(text)
    if not doc.requirements:
        doc.requirements = _requirements_from(text, required=True)
    return doc


def _parse_with_gemini(text: str) -> JDDoc | None:
    data = gemini.generate_json(PROMPT.format(jd=text[:12000]), schema=JDDoc.model_json_schema())
    if not data:
        return None
    try:
        doc = JDDoc.model_validate(data)
    except Exception:  # noqa: BLE001
        return None
    doc.requirements = _normalize_requirements(doc.requirements)
    doc.keywords = [k for k in doc.keywords if k in skill_map()] or [
        r.skill_id for r in doc.requirements if r.skill_id
    ]
    return doc


def _normalize_requirements(reqs: list[Requirement]) -> list[Requirement]:
    """Validate LLM skill ids against the taxonomy and split merged mentions.

    The LLM sometimes returns compound ids such as ``javascript_react``; we re-derive
    canonical ids from the raw text so downstream matching/coverage stays consistent.
    """
    known = skill_map()
    out: list[Requirement] = []
    for req in reqs:
        if req.skill_id and req.skill_id in known:
            ids: list[str | None] = [req.skill_id]
        else:
            ids = [sid for sid, _name, _term in find_skills(req.raw)] or [None]
        for sid in ids:
            if any(existing.skill_id == sid for existing in out):
                continue
            entry = known.get(sid or "", {})
            out.append(
                req.model_copy(
                    update={
                        "skill_id": sid,
                        "type": req.type or ("soft" if entry.get("type") == "soft" else "hard"),
                        "category": req.category or entry.get("category", ""),
                    }
                )
            )
    return out


def _parse_heuristic(text: str) -> JDDoc:
    required_text, optional_text = _split_required_optional(text)
    reqs = _requirements_from(required_text, required=True)
    reqs += [
        r
        for r in _requirements_from(optional_text, required=False)
        if r.skill_id not in {x.skill_id for x in reqs}
    ]
    keywords = [r.skill_id for r in reqs if r.skill_id]
    return JDDoc(
        language=detect_language(text),
        title=_first_line(text),
        seniority=_seniority(text),
        requirements=reqs,
        keywords=keywords,
    )


def _requirements_from(text: str, required: bool) -> list[Requirement]:
    level = 3
    years = _years_required(text)
    if years:
        level = min(5, max(2, years))
    out: list[Requirement] = []
    for sid, name, _term in find_skills(text):
        entry = skill_map().get(sid, {})
        out.append(
            Requirement(
                raw=name,
                skill_id=sid,
                type="soft" if entry.get("type") == "soft" else "hard",
                importance=1.0 if required else 0.5,
                required=required,
                level=level,
                category=entry.get("category", ""),
            )
        )
    return out


def _split_required_optional(text: str) -> tuple[str, str]:
    nice = NICE_RE.search(text)
    if not nice:
        return text, ""
    return text[: nice.start()], text[nice.end() :]


def _first_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip().lstrip("# ").strip()
        if clean:
            return clean
    return ""


def _seniority(text: str) -> str:
    lowered = text.lower()
    for key, value in SENIORITY.items():
        if key in lowered:
            return value
    return "mid"


def _years_required(text: str) -> int:
    m = YEARS_RE.search(text)
    return int(m.group(1)) if m else 0


def requirement_label(skill_id: str) -> str:
    return canonical(skill_id)
