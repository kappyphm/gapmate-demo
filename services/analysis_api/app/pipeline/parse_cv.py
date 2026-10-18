"""Stage 2 — parse CV text into a structured CVDoc (Gemini, else heuristic)."""

import re

from app.llm import gemini
from app.pipeline.normalize import detect_language, normalize_terms, skills_from_text
from app.schemas.cv import (
    Contact,
    CVDoc,
    CVDocMeta,
    EducationItem,
    ExperienceItem,
    SkillItem,
)

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s.\-]{7,}\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com/[^\s)|\]]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"github\.com/[^\s)|\]]+", re.IGNORECASE)
DATE_RANGE_RE = re.compile(
    r"(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|nay|present|hiện tại|now)",
    re.IGNORECASE,
)
SECTION_RE = re.compile(
    r"^#{0,3}\s*(kỹ năng|skills|technical skills|kinh nghiệm|experience|work experience|"
    r"học vấn|education|dự án|projects)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)
EXPERIENCE_HEAD_RE = re.compile(
    r"^#{0,3}\s*(kinh nghiệm|kinh nghiệm làm việc|experience|work experience)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
NEXT_SECTION_RE = re.compile(r"^#{1,2}\s", re.MULTILINE)
ROLE_HEAD_RE = re.compile(r"^\s*#{2,4}\s+(.*\S)\s*$")
BULLET_LINE_RE = re.compile(r"^\s*[-*•▪◦]\s+(.*\S)\s*$")

SENIORITY_KEYWORDS = [
    ("intern", ["thực tập", "intern"]),
    ("junior", ["junior", "fresher"]),
    ("mid", ["middle", "mid-level"]),
    ("senior", ["senior", "sr."]),
    ("lead", ["lead", "trưởng nhóm", "manager", "head of"]),
]

PROMPT = """You are an expert CV parser. Extract structured data from the CV below.
Rules:
- Keep values verbatim from the CV where possible.
- language: "vi" or "en".
- skills: list each mentioned skill with a short evidence span.
- Do NOT invent anything not present.
Respond with a single JSON object.
CV:
---
{cv}
---"""


def parse_cv(text: str) -> CVDoc:
    doc = _parse_with_gemini(text)
    if doc is not None:
        doc.meta.parse_confidence = 0.85
        _fill_contact(doc, text)
        # The LLM may omit sections; union with the deterministic extractor for stable recall.
        doc.skills = _merge_skills(doc.skills, skills_from_text(text))
        if not doc.experience:
            doc.experience = _experience(text)
        if not doc.education:
            doc.education = _education(text)
    else:
        doc = _parse_heuristic(text)
        doc.meta.parse_confidence = 0.6
    if not doc.skills:
        doc.skills = skills_from_text(text)
    return doc


def _merge_skills(primary: list[SkillItem], extra: list[SkillItem]) -> list[SkillItem]:
    merged = list(primary)
    seen = {s.skill_id for s in primary if s.skill_id}
    for skill in extra:
        if skill.skill_id and skill.skill_id not in seen:
            seen.add(skill.skill_id)
            merged.append(skill)
    return merged


def _fill_contact(doc: CVDoc, text: str) -> None:
    """Backfill contact fields the LLM may miss, using cheap deterministic regexes."""
    if not doc.contact.email:
        doc.contact.email = _first(EMAIL_RE, text)
    if not doc.contact.phone:
        doc.contact.phone = _first(PHONE_RE, text)
    if not doc.contact.linkedin:
        doc.contact.linkedin = _first(LINKEDIN_RE, text)
    if not doc.contact.github:
        doc.contact.github = _first(GITHUB_RE, text)
    if not doc.contact.name:
        doc.contact.name = _first_line(text)


def _parse_with_gemini(text: str) -> CVDoc | None:
    data = gemini.generate_json(PROMPT.format(cv=text[:12000]), schema=CVDoc.model_json_schema())
    if not data:
        return None
    try:
        doc = CVDoc.model_validate(data)
    except Exception:  # noqa: BLE001
        return None
    if doc.skills:
        raw = [s.raw for s in doc.skills if not s.skill_id]
        if raw:
            doc.skills = normalize_terms(raw) + [s for s in doc.skills if s.skill_id]
    return doc


def _parse_heuristic(text: str) -> CVDoc:
    contact = Contact(
        name=_first_line(text),
        email=_first(EMAIL_RE, text),
        phone=_first(PHONE_RE, text),
        linkedin=_first(LINKEDIN_RE, text),
        github=_first(GITHUB_RE, text),
    )
    skills = normalize_terms(_skill_section(text)) or skills_from_text(text)
    return CVDoc(
        language=detect_language(text),
        contact=contact,
        summary=_summary(text),
        skills=skills,
        experience=_experience(text),
        education=_education(text),
        meta=CVDocMeta(pages=1, parse_confidence=0.6),
    )


def _first(pattern: re.Pattern, text: str) -> str:
    m = pattern.search(text)
    return m.group(0).strip() if m else ""


def _first_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip().lstrip("# ").strip()
        if clean and not EMAIL_RE.search(clean) and len(clean) < 80:
            return clean
    return ""


def _summary(text: str) -> str:
    m = re.search(r"(mục tiêu|summary|objective|about)[^\n]*\n(.+)", text, re.IGNORECASE)
    return m.group(2).strip()[:400] if m else ""


def _skill_section(text: str) -> list[str]:
    m = re.search(
        r"^#{0,3}\s*(kỹ năng|skills|technical skills)\s*$",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    if not m:
        return []
    rest = text[m.end() :]
    nxt = re.search(r"^#{0,3}\s*\S", rest, re.MULTILINE)
    block = rest[: nxt.start()] if nxt else rest
    parts = re.split(r"[,;•\-\n]", block)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) < 40]


def _experience(text: str) -> list[ExperienceItem]:
    head = EXPERIENCE_HEAD_RE.search(text)
    if not head:
        return []
    rest = text[head.end() :]
    nxt = NEXT_SECTION_RE.search(rest)
    block = rest[: nxt.start()] if nxt else rest

    items: list[ExperienceItem] = []
    current: ExperienceItem | None = None
    for raw in block.splitlines():
        role = ROLE_HEAD_RE.match(raw)
        if role:
            if current is not None:
                items.append(current)
            current = _role_from(role.group(1))
            continue
        bullet = BULLET_LINE_RE.match(raw)
        if bullet and current is not None:
            current.bullets.append(bullet.group(1).strip())
    if current is not None:
        items.append(current)
    return items


def _role_from(text: str) -> ExperienceItem:
    dates = DATE_RANGE_RE.findall(text)
    start, end = dates[0] if dates else ("", "")
    label = DATE_RANGE_RE.sub("", text)
    label = re.sub(r"\([^)]*\)\s*$", "", label).strip(" \t-—–|()")
    company, title = _split_company_title(label)
    return ExperienceItem(
        company=company,
        title=title or label,
        start=start,
        end=end,
        seniority=cv_seniority(text),
        bullets=[],
    )


def _split_company_title(label: str) -> tuple[str, str]:
    for sep in ("—", "–", " - ", "|"):
        if sep in label:
            left, right = label.split(sep, 1)
            return left.strip(" \t-—–|"), right.strip(" \t-—–|")
    return "", label.strip()


def _education(text: str) -> list[EducationItem]:
    degree = ""
    lowered = text.lower()
    for token, label in [
        ("tiến sĩ", "PhD"),
        ("phd", "PhD"),
        ("thạc sĩ", "Master"),
        ("master", "Master"),
        ("cử nhân", "Bachelor"),
        ("bachelor", "Bachelor"),
        ("đại học", "Bachelor"),
        ("university", "Bachelor"),
        ("cao đẳng", "Associate"),
        ("college", "Associate"),
    ]:
        if token in lowered:
            degree = label
            break
    return [EducationItem(degree=degree)] if degree else []


def cv_seniority(text: str) -> str:
    lowered = text.lower()
    for level, keywords in SENIORITY_KEYWORDS:
        if any(k in lowered for k in keywords):
            return level
    return "mid"
