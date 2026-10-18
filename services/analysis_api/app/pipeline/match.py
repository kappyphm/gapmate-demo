"""Stage 5 — match JD requirements against CV skills (cascade, explainable).

Cascade (docs/04 Part A): B1 exact/alias → B3 embedding → B4 LLM adjudication → B5 miss.
`related` skills are not matches (they feed gap adjacency). B3/B4 are skipped automatically
when Gemini is unavailable.
"""

from app.llm import gemini
from app.llm.embeddings import cosine, embed
from app.pipeline.normalize import canonical
from app.schemas.cv import CVDoc, SkillItem
from app.schemas.jd import JDDoc, Requirement
from app.schemas.report import MatchedItem, MissingItem

EXACT_SCORE = 1.0
# `gemini-embedding-001` produces a high similarity baseline (unrelated pairs often score
# ~0.85), so the auto-accept bar is high and the broad band is adjudicated by the LLM
# instead of being accepted outright (docs/04 Part A).
T_HIGH = 0.95
T_MID = 0.88

_ADJUDICATE_PROMPT = """A CV lists the skill "{cv}".
A job requires "{req}".
Answer true ONLY if the CV skill is that exact skill or a widely accepted equivalent.
Knowing a related or adjacent tool is NOT sufficient.
Respond with JSON: {{"match": true|false, "confidence": 0.0-1.0}}"""


def match(jd: JDDoc, cv: CVDoc) -> tuple[list[MatchedItem], list[MissingItem]]:
    cv_by_id = {s.skill_id: s for s in cv.skills if s.skill_id}
    cv_vectors = _cv_vectors(cv)

    matched: list[MatchedItem] = []
    missing: list[MissingItem] = []

    for req in jd.requirements:
        if not req.skill_id:
            continue
        if req.skill_id in cv_by_id:
            item = cv_by_id[req.skill_id]
            matched.append(
                _scored(
                    req.skill_id, EXACT_SCORE, "exact", item.level, req.level, item.evidence_span
                )
            )
            continue
        semantic = _semantic_match(req, cv_vectors)
        if semantic is not None:
            matched.append(semantic)
            continue
        missing.append(
            MissingItem(skill_id=req.skill_id, required=req.required, importance=req.importance)
        )

    return matched, missing


def _cv_vectors(cv: CVDoc) -> list[tuple[SkillItem, list[float]]]:
    vectors: list[tuple[SkillItem, list[float]]] = []
    for skill in cv.skills:
        if not skill.skill_id:
            continue
        vector = embed(canonical(skill.skill_id))
        if vector:
            vectors.append((skill, vector))
    return vectors


def _semantic_match(
    req: Requirement, cv_vectors: list[tuple[SkillItem, list[float]]]
) -> MatchedItem | None:
    if not cv_vectors:
        return None
    req_vector = embed(req.raw or canonical(req.skill_id or ""))
    if req_vector is None:
        return None

    best: tuple[SkillItem, float] | None = None
    for skill, vector in cv_vectors:
        score = cosine(req_vector, vector)
        if best is None or score > best[1]:
            best = (skill, score)
    if best is None:
        return None

    skill, cos = best
    if cos > T_HIGH:
        base = 0.70 + 0.20 * (cos - T_HIGH) / (1 - T_HIGH)
        return _scored(
            req.skill_id or "", base, "semantic", skill.level, req.level, skill.evidence_span
        )
    if cos > T_MID:
        confidence = _llm_adjudicate(req, skill)
        if confidence is not None:
            base = 0.50 + 0.35 * confidence
            return _scored(
                req.skill_id or "", base, "llm", skill.level, req.level, skill.evidence_span
            )
    return None


def _llm_adjudicate(req: Requirement, skill: SkillItem) -> float | None:
    prompt = _ADJUDICATE_PROMPT.format(cv=canonical(skill.skill_id or ""), req=req.raw)
    data = gemini.generate_json(prompt)
    if not data or not data.get("match"):
        return None
    try:
        return max(0.0, min(1.0, float(data.get("confidence", 0.5))))
    except (TypeError, ValueError):
        return 0.5


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
