"""Stage 5 — match JD requirements against CV skills (cascade, explainable)."""

from app.data_loader import skill_map
from app.schemas.cv import CVDoc
from app.schemas.jd import JDDoc
from app.schemas.report import MatchedItem, MissingItem

EXACT_SCORE = 1.0
RELATED_SCORE = 0.85


def match(jd: JDDoc, cv: CVDoc) -> tuple[list[MatchedItem], list[MissingItem]]:
    cv_by_id = {s.skill_id: s for s in cv.skills if s.skill_id}
    cv_ids = set(cv_by_id)

    matched: list[MatchedItem] = []
    missing: list[MissingItem] = []

    for req in jd.requirements:
        if not req.skill_id:
            continue
        if req.skill_id in cv_by_id:
            item = cv_by_id[req.skill_id]
            matched.append(
                _scored(req.skill_id, EXACT_SCORE, "exact", item.level, req.level, item.evidence_span)
            )
            continue
        related = _related_hit(req.skill_id, cv_ids)
        if related:
            item = cv_by_id[related]
            matched.append(
                _scored(req.skill_id, RELATED_SCORE, "alias", item.level, req.level, item.evidence_span)
            )
            continue
        if req.required:
            missing.append(MissingItem(skill_id=req.skill_id, required=True, importance=req.importance))

    return matched, missing


def _related_hit(skill_id: str, cv_ids: set[str]) -> str | None:
    entry = skill_map().get(skill_id, {})
    for rel in entry.get("related", []):
        if rel in cv_ids:
            return rel
    return None


def _scored(
    skill_id: str, base: float, match_type: str, cv_level: int, req_level: int, evidence: str
) -> MatchedItem:
    factor = 1.0 if cv_level >= req_level else 0.6 + 0.4 * (cv_level / max(req_level, 1))
    return MatchedItem(
        skill_id=skill_id,
        match_score=round(base * factor, 3),
        match_type=match_type,
        evidence_span=evidence,
    )
