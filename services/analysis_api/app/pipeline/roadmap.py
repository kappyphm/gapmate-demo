"""Stage 10 — learning roadmap: ordering heuristic + validated AI plan, rule fallback.

Phases build on the Stage 8 gaps: P0 first, adjacent fast wins earlier (docs/04 Part D).
An optional AI plan is accepted only after a per-field validator checks it against the
verified gap/course sets; any mismatch falls back to the deterministic ordering
(docs/07 stage 10, mirroring FitGap's ``validate_learning_roadmap``).
"""

import json

from pydantic import ValidationError

from app.llm import gemini
from app.pipeline.normalize import canonical
from app.schemas.report import CourseRec, GapItem, RoadmapPhase

_PHASE_LABELS = [("0-30 days", "4 weeks"), ("30-60 days", "4 weeks"), ("60-90 days", "4 weeks")]
_ACTIVE_PRIORITIES = ("P0", "P1")

_STRINGS = {
    "en": {
        "apply": "Apply {skills} in a small hands-on project.",
        "cv": "Update your CV with concrete examples of the new skills.",
        "coach": (
            "You are a learning coach. Build a 90-day plan in 3 phases that closes the "
            "skill gaps below.\n"
            "Rules:\n"
            '- Respond with JSON: {{"phases": [{{"phase": "", "duration": "", '
            '"focus_skills": [], "milestones": [], "resources": []}}]}}\n'
            "- focus_skills must come ONLY from the gap skill ids.\n"
            "- resources must come ONLY from the given course ids.\n"
            "- 1-3 focus skills per phase; P0 gaps first; adjacent fast wins early.\n"
            "- milestones: 1-2 concrete actions in {language}; no fabricated credentials."
        ),
    },
    "vi": {
        "apply": "Áp dụng {skills} vào một dự án nhỏ.",
        "cv": "Cập nhật CV với ví dụ cụ thể về kỹ năng mới.",
        "coach": (
            "Bạn là huấn luyện viên học tập. Lên kế hoạch 90 ngày gồm 3 giai đoạn để "
            "bù các kỹ năng còn thiếu dưới đây.\n"
            "Rules:\n"
            '- Respond with JSON: {{"phases": [{{"phase": "", "duration": "", '
            '"focus_skills": [], "milestones": [], "resources": []}}]}}\n'
            "- focus_skills chỉ được lấy từ danh sách gap skill id.\n"
            "- resources chỉ được lấy từ danh sách course id đã cho.\n"
            "- Mỗi giai đoạn 1-3 kỹ năng; ưu tiên P0; kỹ năng liên quan gần lên trước.\n"
            "- milestones: 1-2 hành động cụ thể bằng {language}; không bịa chứng chỉ."
        ),
    },
}

_PLAN_SCHEMA = {
    "type": "object",
    "properties": {"phases": {"type": "array", "items": RoadmapPhase.model_json_schema()}},
    "required": ["phases"],
}


def build_roadmap(
    gaps: list[GapItem],
    *,
    hours_per_week: int = 8,
    language: str = "en",
    courses: list[CourseRec] | tuple[CourseRec, ...] = (),
) -> list[RoadmapPhase]:
    """Build the ordered phase plan (docs/07 stage 10)."""
    ordered = _ordered(gaps)
    if not ordered:
        return []
    if gemini.available():
        plan = _ai_plan(ordered, hours_per_week=hours_per_week, language=language, courses=courses)
        if plan:
            return plan
    return _rule_plan(ordered, hours_per_week=hours_per_week, language=language, courses=courses)


def _hours_for(gap: GapItem) -> float:
    """Heuristic learning cost: fast wins are cheaper, wider level jumps cost more."""
    base = 6.0 if gap.adjacent_to else 10.0
    return base + 2.0 * max(0, gap.target_level - 3)


def _ordered(gaps: list[GapItem]) -> list[GapItem]:
    """P0 before P1; adjacent fast wins first, severity order otherwise kept."""
    active = [g for g in gaps if g.priority in _ACTIVE_PRIORITIES]
    return sorted(active, key=lambda g: (g.priority != "P0", not g.adjacent_to))


def _rule_plan(
    gaps: list[GapItem],
    *,
    hours_per_week: int,
    language: str,
    courses: list[CourseRec] | tuple[CourseRec, ...],
) -> list[RoadmapPhase]:
    capacity = max(1, hours_per_week) * 4
    phases: list[RoadmapPhase] = []
    idx = 0
    for label, default_duration in _PHASE_LABELS:
        budget = float(capacity)
        focus: list[str] = []
        while idx < len(gaps):
            cost = _hours_for(gaps[idx])
            if focus and cost > budget:
                break
            focus.append(gaps[idx].skill_id)
            budget -= cost
            idx += 1
        if focus:
            phases.append(
                RoadmapPhase(
                    phase=label,
                    duration=default_duration,
                    focus_skills=focus,
                    milestones=_milestones(focus, language),
                    resources=_resources(focus, courses),
                )
            )
    return phases


def _milestones(focus: list[str], language: str) -> list[str]:
    strings = _STRINGS.get(language, _STRINGS["en"])
    names = ", ".join(canonical(s) for s in focus)
    return [strings["apply"].format(skills=names), strings["cv"]]


def _resources(focus: list[str], courses: list[CourseRec] | tuple[CourseRec, ...]) -> list[str]:
    ids: list[str] = []
    for course in courses:
        if any(s in focus for s in course.skills_covered) and course.course_id not in ids:
            ids.append(course.course_id)
        if len(ids) >= 3:
            break
    return ids


def _ai_plan(
    gaps: list[GapItem],
    *,
    hours_per_week: int,
    language: str,
    courses: list[CourseRec] | tuple[CourseRec, ...],
) -> list[RoadmapPhase] | None:
    strings = _STRINGS.get(language, _STRINGS["en"])
    prompt = "\n".join(
        [
            strings["coach"].format(language=language),
            f"Hours per week: {max(1, hours_per_week)}",
            "Gaps (skill_id, priority, required level): "
            + json.dumps(
                [
                    {
                        "skill_id": g.skill_id,
                        "priority": g.priority,
                        "level": g.target_level,
                        "adjacent": bool(g.adjacent_to),
                    }
                    for g in gaps[:12]
                ],
                ensure_ascii=False,
            ),
            "Course ids: " + ", ".join(c.course_id for c in courses),
        ]
    )
    data = gemini.generate_json(prompt, schema=_PLAN_SCHEMA, temperature=0.2)
    gap_ids = {g.skill_id for g in gaps}
    course_ids = {c.course_id for c in courses}
    return _validate_plan(data, gap_ids=gap_ids, course_ids=course_ids, language=language)


def _validate_plan(
    data: dict | None, *, gap_ids: set[str], course_ids: set[str], language: str
) -> list[RoadmapPhase] | None:
    """Accept only plans whose focus/resources are subsets of the verified sets."""
    raw = data.get("phases") if isinstance(data, dict) else None
    if not isinstance(raw, list) or not 1 <= len(raw) <= len(_PHASE_LABELS):
        return None
    phases: list[RoadmapPhase] = []
    for idx, entry in enumerate(raw):
        if not isinstance(entry, dict):
            return None
        try:
            phase = RoadmapPhase.model_validate(entry)
        except ValidationError:
            return None
        focus = [s for s in phase.focus_skills if s in gap_ids]
        if not focus:
            continue
        label, duration = _PHASE_LABELS[idx]
        milestones = [m for m in phase.milestones if isinstance(m, str) and m.strip()][:3]
        resources = [r for r in phase.resources if r in course_ids][:3]
        phases.append(
            RoadmapPhase(
                phase=label,
                duration=phase.duration or duration,
                focus_skills=focus,
                milestones=milestones or _milestones(focus, language),
                resources=resources,
            )
        )
    return phases or None
