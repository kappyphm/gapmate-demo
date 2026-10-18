"""Stage 11 — course recommendation: deterministic gap → catalog match (+ AI rerank).

Deterministic ranking (docs/07 stage 11): skill overlap weighted by gap importance and
priority, plus level and language fit. An optional AI rerank only *orders* the
deterministic shortlist and is validated back against it; any mismatch keeps the
deterministic order.
"""

from app.data_loader import load_courses
from app.llm import gemini
from app.pipeline.normalize import canonical
from app.schemas.report import CourseRec, GapItem

MAX_SHORTLIST = 16

_STRINGS = {
    "en": {
        "covers": "Covers {skills} ({priorities}).",
    },
    "vi": {
        "covers": "Bao gồm {skills} ({priorities}).",
    },
}


def recommend_courses(
    gaps: list[GapItem], *, language: str = "en", limit: int = 8
) -> list[CourseRec]:
    """Rank the course catalog against the prioritized gaps (docs/07 stage 11)."""
    if not gaps or limit < 1:
        return []
    gap_by_id = {g.skill_id: g for g in gaps}
    ranked = _rank(gap_by_id, language=language)
    if gemini.available() and len(ranked) > 1:
        ranked = _rerank_ai(ranked[:MAX_SHORTLIST], gaps) + ranked[MAX_SHORTLIST:]
    return [_to_rec(course, gap_by_id, language) for course in ranked[:limit]]


def _rank(gap_by_id: dict[str, GapItem], *, language: str) -> list[dict]:
    scored: list[tuple[float, float, dict]] = []
    for course in load_courses():
        hits = [s for s in course.get("skills_covered", []) if s in gap_by_id]
        if not hits:
            continue
        score = sum(gap_by_id[s].importance for s in hits)
        score += 0.5 * sum(1 for s in hits if gap_by_id[s].priority == "P0")
        target = max(gap_by_id[s].target_level or 3 for s in hits)
        want = "beginner" if target <= 2 else "intermediate" if target == 3 else "advanced"
        level = course.get("level", "")
        if level == want:
            score += 0.3
        elif abs(_level_rank(level) - _level_rank(want)) == 1:
            score += 0.15
        if course.get("language") == language:
            score += 0.2
        scored.append((score, float(course.get("rating") or 0.0), course))
    scored.sort(key=lambda t: (-t[0], -t[1]))
    return [course for _score, _rating, course in scored]


def _rerank_ai(courses: list[dict], gaps: list[GapItem]) -> list[dict]:
    by_id = {c["course_id"]: c for c in courses}
    gap_lines = [
        f"- {g.skill_id}: priority {g.priority}, importance {round(g.importance, 2)}"
        for g in gaps[:12]
    ]
    ids = [c["course_id"] for c in courses]
    prompt = (
        "Order these courses by usefulness for closing the skill gaps.\n"
        "Rules:\n"
        '- Respond with JSON: {"course_ids": [...]}\n'
        "- course_ids must be a permutation of the given ids (you may drop some, "
        "but must not invent or reorder beyond usefulness).\n"
        "Gaps:\n" + "\n".join(gap_lines) + "\nCourses:\n" + ", ".join(ids)
    )
    data = gemini.generate_json(prompt, temperature=0.0)
    if not data:
        return courses
    raw = data.get("course_ids")
    if not isinstance(raw, list):
        return courses
    ordered_ids = [cid for cid in raw if cid in by_id]
    if not ordered_ids:
        return courses
    ordered = [by_id[cid] for cid in ordered_ids]
    seen = set(ordered_ids)
    return ordered + [c for c in courses if c["course_id"] not in seen]


def _to_rec(course: dict, gap_by_id: dict[str, GapItem], language: str) -> CourseRec:
    hits = [s for s in course.get("skills_covered", []) if s in gap_by_id]
    strings = _STRINGS.get(language, _STRINGS["en"])
    names = ", ".join(canonical(s) for s in hits)
    priorities = ", ".join(sorted({gap_by_id[s].priority for s in hits}))
    return CourseRec(
        course_id=course.get("course_id", ""),
        title=course.get("title", ""),
        provider=course.get("provider", ""),
        skills_covered=list(course.get("skills_covered", [])),
        match_reason=strings["covers"].format(skills=names, priorities=priorities),
        url=course.get("url", ""),
        duration=f"{course.get('duration_hours', 0)}h",
    )


def _level_rank(level: str) -> int:
    return {"beginner": 1, "intermediate": 2, "advanced": 3}.get(level, 2)
