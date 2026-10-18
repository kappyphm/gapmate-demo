"""Stage 7 — deterministic ATS rules engine (docs/04 Part C).

Each rule returns ``{code, severity, weight, pass, message, fix}`` and the ATS score is
``100 * sum(weight * pass) / sum(weight)``. Rules never call the LLM; layout facts come from
Stage 1 (``extract``) via the ``layout`` dict and the parsed ``CVDoc``.
"""

import re

from app.data_loader import find_skills, skill_map
from app.pipeline.normalize import canonical
from app.schemas.cv import CVDoc
from app.schemas.jd import JDDoc
from app.schemas.report import AtsIssue, AtsSection, KeywordCoverage

SEVERITY_WEIGHT = {"critical": 3, "warn": 2, "info": 1}

_COVERAGE_THRESHOLD = 0.6
_MAX_KEYWORD_DENSITY = 0.05

_HEADINGS = {
    "summary": ["summary", "objective", "about", "mục tiêu", "tóm tắt", "giới thiệu"],
    "experience": ["experience", "work experience", "employment", "kinh nghiệm"],
    "education": ["education", "học vấn", "học tập"],
    "skills": ["skills", "technical skills", "kỹ năng"],
}

_DATE_RE = re.compile(r"\b(\d{1,2}/\d{4}|\d{4})\b")
_BULLET_RE = re.compile(r"^\s*[-*•▪◦]\s+(.*\S)\s*$", re.MULTILINE)
_QUANT_RE = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(%|percent|users?|customers?|clients?|ms|seconds?|"
    r"minutes?|hours?|days?|weeks?|months?|x|k|triệu|nghìn|người|giây|phút)\b",
    re.IGNORECASE,
)
_ACRONYM_RE = re.compile(r"([A-Z][A-Za-z.]+(?:\s[A-Z][A-Za-z.]+)*)\s*\(([A-Z]{2,})\)")

_ACTION_VERBS = {
    "built",
    "build",
    "developed",
    "develop",
    "designed",
    "design",
    "created",
    "create",
    "implemented",
    "implement",
    "led",
    "lead",
    "managed",
    "manage",
    "improved",
    "improve",
    "reduced",
    "reduce",
    "increased",
    "increase",
    "migrated",
    "migrate",
    "launched",
    "launch",
    "optimized",
    "optimise",
    "optimize",
    "delivered",
    "deliver",
    "automated",
    "automate",
    "phát triển",
    "xây dựng",
    "thiết kế",
    "triển khai",
    "tối ưu",
    "cải thiện",
    "quản lý",
    "tạo",
    "viết",
    "hỗ trợ",
    "phối hợp",
    "chuyển đổi",
    "thực hiện",
    "đảm nhận",
    "đã",
}

_SUPPORTED_FILES = {"pdf", "docx", "doc", "txt", "md", "text"}


def run_ats(
    cv: CVDoc,
    jd: JDDoc,
    *,
    text: str = "",
    layout: dict | None = None,
    matched_ids: set[str] | None = None,
) -> AtsSection:
    layout = layout or {}
    text = text or ""
    matched_ids = matched_ids or set()
    issues = (
        _group_a(cv, text, layout)
        + _group_b(cv, text, layout)
        + _group_c(cv, jd, text, matched_ids)
    )
    coverage = _keyword_coverage(cv, jd, text, matched_ids)
    score = _score(issues)
    return AtsSection(
        score=score,
        issues=issues,
        keyword_coverage=coverage,
        format_issues=[i.code for i in issues if not i.passed and i.code.startswith("A")],
    )


def _issue(code: str, severity: str, passed: bool, message: str, fix: str) -> AtsIssue:
    return AtsIssue(
        code=code,
        severity=severity,
        weight=SEVERITY_WEIGHT.get(severity, 1),
        passed=passed,
        message=message,
        fix=fix,
    )


def _score(issues: list[AtsIssue]) -> int:
    total = sum(i.weight for i in issues)
    if not total:
        return 0
    passed = sum(i.weight for i in issues if i.passed)
    return int(round(100 * passed / total))


# --- Group A — Parseability -------------------------------------------------


def _group_a(cv: CVDoc, text: str, layout: dict) -> list[AtsIssue]:
    file_type = str(layout.get("file_type", "txt")).lower().lstrip(".")
    used_ocr = bool(layout.get("used_ocr", False))
    has_text = bool(layout.get("has_text", bool(text.strip())))

    out = [
        _issue(
            "A1",
            "critical",
            file_type in _SUPPORTED_FILES,
            f"File type '{file_type or 'unknown'}'."
            + ("" if file_type in _SUPPORTED_FILES else " Not a supported format."),
            "Submit as PDF or DOCX (text-based, not scanned).",
        ),
    ]

    if has_text and text.strip():
        msg = "Document text is machine-readable."
        if used_ocr:
            msg = "Scanned CV — text recovered via OCR; a text-based version parses better."
        out.append(_issue("A2", "critical", True, msg, "Prefer an export with selectable text."))
    else:
        out.append(
            _issue(
                "A2",
                "critical",
                False,
                "No extractable text found (scanned/image-only document).",
                "Export the CV with a real text layer (PDF/DOCX), not a photo/scan.",
            )
        )

    out.append(
        _issue(
            "A3",
            "critical",
            bool(layout.get("single_column", True)),
            "Layout is single-column."
            if layout.get("single_column", True)
            else "Multi-column layout detected.",
            "Use a single-column layout; ATS parsers read columns out of order.",
        )
    )
    out.append(
        _issue(
            "A4",
            "warn",
            not bool(layout.get("has_tables", False)),
            "No layout tables detected."
            if not layout.get("has_tables", False)
            else "Tables used for layout.",
            "Avoid tables for page layout; use a plain list instead.",
        )
    )
    out.append(
        _issue(
            "A5",
            "warn",
            not bool(layout.get("header_footer_content", False)),
            "No critical content in header/footer."
            if not layout.get("header_footer_content", False)
            else "Critical content found in header/footer.",
            "Move contact details and section text into the document body.",
        )
    )

    has_contact = bool(cv.contact.email or cv.contact.phone)
    out.append(
        _issue(
            "A6",
            "warn",
            has_contact,
            "Contact details are text."
            if has_contact
            else "Contact details may be embedded in an image or icon font.",
            "Type email/phone as plain text so ATS can read them.",
        )
    )
    out.append(
        _issue(
            "A7",
            "info",
            bool(layout.get("standard_fonts", True)),
            "Standard fonts used."
            if layout.get("standard_fonts", True)
            else "Non-standard fonts detected.",
            "Stick to common fonts (Arial, Calibri, Times New Roman).",
        )
    )
    out.append(
        _issue(
            "A8",
            "info",
            not bool(layout.get("has_text_boxes", False)),
            "No content in text boxes."
            if not layout.get("has_text_boxes", False)
            else "Content inside text boxes detected.",
            "Move text out of boxes/floating frames into the normal flow.",
        )
    )
    return out


# --- Group B — Structure ----------------------------------------------------


def _group_b(cv: CVDoc, text: str, layout: dict) -> list[AtsIssue]:
    lowered = text.lower()
    present = sum(1 for terms in _HEADINGS.values() if any(t in lowered for t in terms))
    out = [
        _issue(
            "B1",
            "warn",
            present >= 2,
            f"{present}/4 standard section headings found.",
            "Use standard headings: Summary, Experience, Education, Skills.",
        )
    ]

    dates = _DATE_RE.findall(text)
    formats = {("mm_yyyy" if "/" in d else "yyyy") for d in dates}
    # MM/YYYY for roles plus bare years for education is a normal, consistent CV.
    consistent = len(formats) <= 1 or formats == {"mm_yyyy", "yyyy"}
    out.append(
        _issue(
            "B2",
            "warn",
            consistent,
            "Date formats are consistent." if consistent else "Mixed date formats detected.",
            "Use one consistent date format, e.g. MM/YYYY.",
        )
    )

    has_contact = bool(cv.contact.email and cv.contact.phone)
    detail = ", ".join(
        part for part, ok in (("email", cv.contact.email), ("phone", cv.contact.phone)) if ok
    )
    out.append(
        _issue(
            "B3",
            "critical",
            has_contact,
            f"Reachable contact info present ({detail})." if detail else "Missing email/phone.",
            "Add a plain-text email and phone number at the top.",
        )
    )

    has_title = any(e.title for e in cv.experience)
    out.append(
        _issue(
            "B4",
            "warn",
            has_title,
            "Job titles present." if has_title else "No clear job title found.",
            "Give each role a clear, standard job title.",
        )
    )

    has_bullets = bool(_BULLET_RE.search(text))
    out.append(
        _issue(
            "B5",
            "info",
            has_bullets,
            "Bullet points used." if has_bullets else "No bullet points found.",
            "Use bullet points for achievements instead of paragraphs.",
        )
    )

    pages = int(layout.get("pages", 1) or 1)
    out.append(
        _issue(
            "B6",
            "info",
            1 <= pages <= 2,
            f"{pages} page(s)."
            if 1 <= pages <= 2
            else f"{pages} pages — outside the 1–2 page range.",
            "Keep the CV to 1–2 pages.",
        )
    )
    return out


# --- Group C — Content / keywords ------------------------------------------


def _group_c(
    cv: CVDoc, jd: JDDoc, text: str, matched_ids: set[str] | None = None
) -> list[AtsIssue]:
    coverage = _keyword_coverage(cv, jd, text, matched_ids)
    total = len(coverage.matched) + len(coverage.missing)
    ratio = len(coverage.matched) / total if total else 1.0
    out = [
        _issue(
            "C1",
            "warn",
            ratio >= _COVERAGE_THRESHOLD,
            f"JD keyword coverage {int(round(ratio * 100))}% ({len(coverage.matched)}/{total}).",
            "Work the missing JD keywords into your skills/bullets where truthful.",
        )
    ]

    stuffed = _stuffed_keywords(cv, text)
    out.append(
        _issue(
            "C2",
            "warn",
            not stuffed,
            "Keyword density looks natural."
            if not stuffed
            else f"Keyword stuffing: {', '.join(stuffed)}.",
            "Use keywords naturally; repeat a term only where it fits.",
        )
    )

    bullets = _bullets(cv, text)
    has_verbs = any(_starts_with_verb(b) for b in bullets)
    out.append(
        _issue(
            "C3",
            "info",
            has_verbs or not bullets,
            "Action verbs used." if has_verbs else "Bullets lack strong action verbs.",
            "Start each bullet with an action verb (Built, Led, Improved…).",
        )
    )

    has_metrics = any(_QUANT_RE.search(b) for b in bullets)
    out.append(
        _issue(
            "C4",
            "info",
            has_metrics,
            "Quantified achievements present."
            if has_metrics
            else "No quantified achievements found.",
            "Add metrics (%, users, time saved) or a [placeholder] to fill later.",
        )
    )

    pairs = _ACRONYM_RE.findall(text)
    # We can only verify acronyms we can detect as "Full form (ACR)"; with no pairs to
    # check there is nothing missing, so the rule passes.
    has_acronym = bool(pairs) and all(
        _mentions_both(text, full, acronym) for full, acronym in pairs
    )
    out.append(
        _issue(
            "C5",
            "info",
            has_acronym or not pairs,
            "Acronym defined with full form."
            if has_acronym
            else "No acronyms to spell out."
            if not pairs
            else "Acronyms used without full form.",
            'Spell out acronyms once, e.g. "JavaScript (JS)".',
        )
    )

    out.append(
        _issue(
            "C6",
            "info",
            True,
            "Basic spell/grammar check not run (no dictionary configured).",
            "Proofread manually; spelling errors can hurt ATS matching.",
        )
    )
    return out


# --- Keyword coverage -------------------------------------------------------


def _keyword_coverage(
    cv: CVDoc, jd: JDDoc, text: str, matched_ids: set[str] | None = None
) -> KeywordCoverage:
    matched_ids = matched_ids or set()
    ids: list[str] = []
    for req in jd.requirements:
        if req.skill_id:
            ids.append(req.skill_id)
    for keyword in jd.keywords:
        if not keyword:
            continue
        if skill_map().get(keyword):
            ids.append(keyword)
            continue
        matches = find_skills(keyword)
        if matches:
            ids.append(matches[0][0])

    cv_ids = {s.skill_id for s in cv.skills if s.skill_id}
    lowered = text.lower()

    matched: list[str] = []
    missing: list[str] = []
    seen: set[str] = set()
    for skill_id in ids:
        name = canonical(skill_id)
        if name in seen:
            continue
        seen.add(name)
        if skill_id in cv_ids or skill_id in matched_ids or name.lower() in lowered:
            matched.append(name)
        else:
            missing.append(name)
    return KeywordCoverage(matched=matched, missing=missing)


def _stuffed_keywords(cv: CVDoc, text: str) -> list[str]:
    words = re.findall(r"\w+", text.lower())
    total = len(words) or 1
    out: list[str] = []
    for skill in cv.skills:
        if not skill.skill_id:
            continue
        name = canonical(skill.skill_id)
        if lowered_count(text, name) / total > _MAX_KEYWORD_DENSITY:
            out.append(name)
    return out


def lowered_count(text: str, term: str) -> int:
    return len(re.findall(re.escape(term.lower()), text.lower()))


def _mentions_both(text: str, full: str, acronym: str) -> bool:
    lowered = text.lower()
    return full.lower() in lowered and acronym.lower() in lowered


def _bullets(cv: CVDoc, text: str) -> list[str]:
    lines = [b.strip() for exp in cv.experience for b in exp.bullets if b.strip()]
    if lines:
        return lines
    return [m.group(1).strip() for m in _BULLET_RE.finditer(text)]


def _starts_with_verb(bullet: str) -> bool:
    clean = re.sub(r"^[-*•▪◦\s]+", "", bullet).lower()
    return any(clean.startswith(v) for v in _ACTION_VERBS)
