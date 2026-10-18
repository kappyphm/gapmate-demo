"""Stage 8 — deterministic gap prioritization (docs/04 Part D).

gap_severity = importance_jd · (1 - final_i) · (required ? 1.0 : 0.6)

Severity is naturally in [0, 1] (importance is normalized) and bucketed:
P0 must-close (required, high severity), P1 nice-to-have, P2 already strong.
Learning adjacency (taxonomy ``related`` skills the CV already has) marks fast wins.
AI re-ranking is intentionally not applied here: priority is a fact, not a judgment
(docs/07 stage 8 — AI may only re-rank/explain, and the deterministic order wins).
"""

from app.data_loader import skill_map
from app.schemas.cv import SkillItem
from app.schemas.jd import JDDoc
from app.schemas.report import GapItem, MatchedItem

REQUIRED_FACTOR = 1.0
OPTIONAL_FACTOR = 0.6
P0_SEVERITY = 0.5
P1_SEVERITY = 0.15
_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}

_STRINGS = {
    "en": {
        "required": "Required by the JD (importance {importance}) — no evidence in the CV.",
        "optional": "Nice-to-have (importance {importance}) — not evidenced in the CV yet.",
        "level": "CV level {current} is below the JD target level {target}.",
    },
    "vi": {
        "required": "JD yêu cầu (mức quan trọng {importance}) — CV chưa có bằng chứng.",
        "optional": "Ưu tiên (mức quan trọng {importance}) — CV chưa thể hiện.",
        "level": "Cấp độ CV ({current}) thấp hơn mức JD yêu cầu ({target}).",
    },
}


def build_gaps(
    jd: JDDoc,
    matched: list[MatchedItem],
    cv_skills: list[SkillItem],
    *,
    language: str = "en",
) -> list[GapItem]:
    """Return JD requirements that are not fully satisfied, prioritized (docs/04 Part D)."""
    matched_by_id = {m.skill_id: m.match_score for m in matched if m.skill_id}
    cv_levels = {s.skill_id: s.level for s in cv_skills if s.skill_id}
    strings = _STRINGS.get(language, _STRINGS["en"])

    scored: list[tuple[str, float]] = []
    for req in jd.requirements:
        if not req.skill_id:
            continue
        final_i = matched_by_id.get(req.skill_id, 0.0)
        if final_i >= 1.0:
            continue
        factor = REQUIRED_FACTOR if req.required else OPTIONAL_FACTOR
        severity = req.importance * (1.0 - final_i) * factor
        if severity > 0.0:
            scored.append((req.skill_id, severity))

    severity_by_id = dict(scored)
    out: list[GapItem] = []
    for req in jd.requirements:
        if not req.skill_id:
            continue
        severity = severity_by_id.get(req.skill_id)
        if severity is None:
            continue
        current = cv_levels.get(req.skill_id, 0)
        adjacent = [
            rel for rel in skill_map().get(req.skill_id, {}).get("related", []) if rel in cv_levels
        ]
        if current > 0:
            reason = strings["level"].format(current=current, target=req.level)
        elif req.required:
            reason = strings["required"].format(importance=round(req.importance, 2))
        else:
            reason = strings["optional"].format(importance=round(req.importance, 2))
        out.append(
            GapItem(
                skill_id=req.skill_id,
                importance=req.importance,
                current_level=current,
                target_level=req.level,
                priority=_bucket(severity, required=req.required),
                reason=reason,
                adjacent_to=adjacent,
            )
        )
    out.sort(key=lambda g: (_PRIORITY_ORDER[g.priority], -severity_by_id[g.skill_id]))
    return out


def _bucket(severity: float, *, required: bool) -> str:
    if required and severity >= P0_SEVERITY:
        return "P0"
    if severity >= P1_SEVERITY:
        return "P1"
    return "P2"
