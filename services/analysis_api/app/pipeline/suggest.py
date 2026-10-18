"""Stage 9 (P2 subset) — deterministic rewrite suggestions + before/after ATS projection.

Guardrails (docs/04 Part E): never invent experience/skills; surface placeholders ``[…]`` for
missing metrics via ``needs_user_input``; improve content that already exists. Skills the CV does
not have are **not** added here — they belong to the gap/roadmap stage (P3).

Suggestions are localized to the CV language (Vietnamese or English).
"""

from app.pipeline.ats import _BULLET_RE, _QUANT_RE, _starts_with_verb, run_ats
from app.pipeline.normalize import detect_language
from app.schemas.cv import CVDoc
from app.schemas.jd import JDDoc
from app.schemas.report import AtsPreview, AtsSection, SuggestionItem

_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "metric_reason": "Quantified achievements read better and pass ATS content checks.",
        "metric_suffix": " — [add a metric such as 30% or 2k users]",
        "verb_reason": "Open the bullet with a strong action verb for impact.",
        "verb_prefix": "Delivered ",
        "b1_improved": "## Summary",
        "b1_reason": "Add a standard heading so the ATS can classify this section.",
        "b3_improved": "- Email: [your email]\n- Phone: [your phone]",
        "b3_reason": "Most ATS require a plain-text email and phone.",
        "b4_improved": "- [Job Title] — Company (MM/YYYY – MM/YYYY)",
        "b4_reason": "Use a standard job title so the ATS maps the role.",
        "b5_improved": "## Experience\n- [achievement starting with an action verb]",
        "b5_reason": "Bullet points map cleanly to ATS fields.",
    },
    "vi": {
        "metric_reason": "Thành tích có số liệu thuyết phục hơn và giúp vượt các kiểm tra nội dung ATS.",
        "metric_suffix": " — [bổ sung số liệu, ví dụ 30% hoặc 1.000 người dùng]",
        "verb_reason": "Bắt đầu mỗi gạch đầu dòng bằng động từ mạnh để tạo ấn tượng.",
        "verb_prefix": "Đã ",
        "b1_improved": "## Tóm tắt",
        "b1_reason": "Thêm tiêu đề chuẩn để ATS phân loại được nội dung.",
        "b3_improved": "- Email: [email của bạn]\n- Điện thoại: [số điện thoại]",
        "b3_reason": "Hầu hết ATS cần email và số điện thoại ở dạng văn bản.",
        "b4_improved": "- [Chức danh] — Công ty (MM/YYYY – MM/YYYY)",
        "b4_reason": "Dùng chức danh chuẩn để ATS nhận diện đúng vị trí.",
        "b5_improved": "## Kinh nghiệm\n- [thành tích bắt đầu bằng động từ mạnh]",
        "b5_reason": "Gạch đầu dòng giúp ATS trích xuất thông tin chính xác.",
    },
}

_LAYOUT_FIX = {
    "vi": {
        "A1": "Nộp CV dạng PDF hoặc DOCX (có lớp văn bản, không phải ảnh scan).",
        "A2": "Xuất CV có lớp văn bản thật (PDF/DOCX), không dùng ảnh chụp/bản scan.",
        "A3": "Dùng bố cục một cột; ATS đọc nhiều cột không đúng thứ tự.",
        "A4": "Tránh dùng bảng để dàn trang; dùng danh sách thường.",
        "A5": "Đưa thông tin liên hệ và nội dung chính vào phần thân tài liệu.",
        "A6": "Gõ email/số điện thoại dạng văn bản để ATS đọc được.",
        "A7": "Chỉ dùng font phổ biến (Arial, Calibri, Times New Roman).",
        "A8": "Đưa chữ ra khỏi text box/khung nổi vào luồng văn bản bình thường.",
    }
}


def build_suggestions(cv: CVDoc, ats: AtsSection, *, text: str = "") -> list[SuggestionItem]:
    lang = detect_language(text)
    out: list[SuggestionItem] = []
    out.extend(_content_suggestions(cv, text, lang))
    out.extend(_structure_suggestions(ats, lang))
    out.extend(_layout_suggestions(ats, lang))
    return out[:8]


def project_ats(
    cv: CVDoc,
    jd: JDDoc,
    *,
    text: str,
    layout: dict | None,
    suggestions: list[SuggestionItem],
    before: int,
    matched_ids: set[str] | None = None,
) -> AtsPreview:
    """Re-run the ruleset assuming the suggested edits are applied.

    Only edits to content already present are projected (no new skills), honoring the
    "never invent skills" guardrail.
    """
    replacements = {
        s.original: s.improved
        for s in suggestions
        if s.original and s.improved and not s.code.startswith("A")
    }
    appended = [
        s.improved
        for s in suggestions
        if s.improved and not s.original and not s.code.startswith("A")
    ]

    new_experience = [
        exp.model_copy(update={"bullets": [replacements.get(b.strip(), b) for b in exp.bullets]})
        for exp in cv.experience
    ]
    if any(s.code == "B4" for s in suggestions) and new_experience:
        new_experience[0] = new_experience[0].model_copy(update={"title": "[Job Title]"})
    new_cv = cv.model_copy(update={"experience": new_experience})

    new_text = text
    for original, improved in replacements.items():
        if original in new_text:
            new_text = new_text.replace(original, improved, 1)
    if appended:
        new_text = new_text + "\n" + "\n".join(appended)

    after = run_ats(new_cv, jd, text=new_text, layout=layout, matched_ids=matched_ids).score
    return AtsPreview(before=before, after=max(before, after))


def _content_suggestions(cv: CVDoc, text: str, lang: str) -> list[SuggestionItem]:
    bullets = [b.strip() for exp in cv.experience for b in exp.bullets if b.strip()]
    if not bullets:
        bullets = [m.group(1).strip() for m in _BULLET_RE.finditer(text)]
    if not bullets:
        return []

    strings = _STRINGS[lang]
    out: list[SuggestionItem] = []

    plain = next((b for b in bullets if not _QUANT_RE.search(b)), None)
    if plain:
        out.append(
            SuggestionItem(
                section="experience.bullets",
                original=plain,
                improved=plain.rstrip(". ") + strings["metric_suffix"],
                reason=strings["metric_reason"],
                jd_keywords_addressed=[],
                needs_user_input=["metric"],
                code="C4",
            )
        )

    weak = next((b for b in bullets if not _starts_with_verb(b)), None)
    if weak:
        out.append(
            SuggestionItem(
                section="experience.bullets",
                original=weak,
                improved=_with_verb(weak, strings["verb_prefix"]),
                reason=strings["verb_reason"],
                jd_keywords_addressed=[],
                needs_user_input=[],
                code="C3",
            )
        )
    return out


def _structure_suggestions(ats: AtsSection, lang: str) -> list[SuggestionItem]:
    failed = {i.code for i in ats.issues if not i.passed}
    strings = _STRINGS[lang]
    out: list[SuggestionItem] = []
    if "B1" in failed:
        out.append(
            SuggestionItem(
                section="summary",
                original="",
                improved=strings["b1_improved"],
                reason=strings["b1_reason"],
                jd_keywords_addressed=[],
                needs_user_input=["summary_text"],
                code="B1",
            )
        )
    if "B3" in failed:
        out.append(
            SuggestionItem(
                section="contact",
                original="",
                improved=strings["b3_improved"],
                reason=strings["b3_reason"],
                jd_keywords_addressed=[],
                needs_user_input=["email", "phone"],
                code="B3",
            )
        )
    if "B4" in failed:
        out.append(
            SuggestionItem(
                section="experience",
                original="",
                improved=strings["b4_improved"],
                reason=strings["b4_reason"],
                jd_keywords_addressed=[],
                needs_user_input=["job_title"],
                code="B4",
            )
        )
    if "B5" in failed:
        out.append(
            SuggestionItem(
                section="experience",
                original="",
                improved=strings["b5_improved"],
                reason=strings["b5_reason"],
                jd_keywords_addressed=[],
                needs_user_input=["experience"],
                code="B5",
            )
        )
    return out


def _layout_suggestions(ats: AtsSection, lang: str) -> list[SuggestionItem]:
    fixes = _LAYOUT_FIX.get(lang, {})
    out: list[SuggestionItem] = []
    for issue in ats.issues:
        if issue.passed or not issue.code.startswith("A"):
            continue
        out.append(
            SuggestionItem(
                section="layout",
                original="",
                improved=fixes.get(issue.code, issue.fix),
                reason=issue.message,
                jd_keywords_addressed=[],
                needs_user_input=[],
                code=issue.code,
            )
        )
    return out


def _with_verb(bullet: str, prefix: str) -> str:
    clean = bullet.lstrip("-*•▪◦ ").strip()
    if not clean:
        return f"{prefix}[…]"
    return f"{prefix}{clean[0].lower() + clean[1:]}"
