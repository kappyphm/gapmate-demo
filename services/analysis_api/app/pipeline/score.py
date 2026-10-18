"""Stage 6 — compute subscores + overall match score (rubric in docs/04)."""

from datetime import date

from app.schemas.cv import CVDoc
from app.schemas.jd import JDDoc
from app.schemas.report import MatchedItem, MatchResult, MatchSubscores, MissingItem

WEIGHTS = {"skills": 0.40, "experience": 0.30, "education": 0.15, "keywords": 0.15}
MUST_HAVE_PENALTY = 0.85
SENIORITY_RANK = {"intern": 1, "junior": 2, "mid": 3, "senior": 4, "lead": 5}
DEGREE_RANK = {"Associate": 2, "Bachelor": 3, "Master": 4, "PhD": 5}


def score(
    cv: CVDoc,
    jd: JDDoc,
    matched: list[MatchedItem],
    missing: list[MissingItem],
    *,
    cv_seniority: str,
    mode: str,
    parse_confidence: float,
) -> MatchResult:
    subs = MatchSubscores(
        skills=_skills_score(jd, matched, missing),
        experience=_experience_score(cv, jd, cv_seniority),
        education=_education_score(cv),
        keywords=_keywords_score(jd, matched),
    )
    overall = sum(WEIGHTS[k] * getattr(subs, k) for k in WEIGHTS)
    return MatchResult(
        overall=int(round(max(0.0, min(100.0, overall)))),
        subscores=subs,
        matched=matched,
        missing=missing,
        evidence=[m.evidence_span for m in matched if m.evidence_span][:10],
    )


def _skills_score(jd: JDDoc, matched: list[MatchedItem], missing: list[MissingItem]) -> float:
    reqs = [r for r in jd.requirements if r.skill_id]
    if not reqs:
        return 0.0
    matched_by_id = {m.skill_id: m.match_score for m in matched}
    total_w = sum(r.importance for r in reqs)
    got = sum(r.importance * matched_by_id.get(r.skill_id, 0.0) for r in reqs)
    score = 100.0 * got / total_w if total_w else 0.0
    if any(m.required for m in missing):
        score *= MUST_HAVE_PENALTY
    return round(score, 1)


def _experience_score(cv: CVDoc, jd: JDDoc, cv_seniority: str) -> float:
    years = _cv_years(cv)
    required = _required_years(jd)
    years_fit = min(years / required, 1.0) if required else min(years / 3.0, 1.0)
    seniority_fit = (
        1.0 if SENIORITY_RANK.get(cv_seniority, 3) >= SENIORITY_RANK.get(jd.seniority, 3) else 0.6
    )
    relevance = 0.7
    return round(100.0 * (0.40 * years_fit + 0.35 * relevance + 0.25 * seniority_fit), 1)


def _education_score(cv: CVDoc) -> float:
    rank = max((DEGREE_RANK.get(e.degree, 0) for e in cv.education), default=0)
    return round(100.0 * (1.0 if rank >= 3 else 0.7 if rank > 0 else 0.6), 1)


def _keywords_score(jd: JDDoc, matched: list[MatchedItem]) -> float:
    reqs = [r for r in jd.requirements if r.skill_id]
    if not reqs:
        return 0.0
    matched_ids = {m.skill_id for m in matched}
    covered = sum(1 for r in reqs if r.skill_id in matched_ids)
    return round(100.0 * covered / len(reqs), 1)


def _cv_years(cv: CVDoc) -> float:
    total = 0.0
    for exp in cv.experience:
        start = _to_month(exp.start)
        end = _to_month(exp.end) or date.today()
        if start and end and end >= start:
            total += (end.year - start.year) * 12 + (end.month - start.month) + 1
    return round(total / 12.0, 1)


def _required_years(jd: JDDoc) -> float:
    levels = [r.level for r in jd.requirements if r.required]
    return float(max(levels)) if levels else 3.0


def _to_month(value: str) -> date | None:
    value = (value or "").strip().lower()
    if not value or value in {"nay", "present", "now", "hiện tại"}:
        return None
    if "/" in value:
        parts = value.split("/")
        if len(parts) == 2 and parts[0].isdigit():
            return date(int(parts[1]), max(1, min(12, int(parts[0]))), 1)
    if value.isdigit() and len(value) == 4:
        return date(int(value), 1, 1)
    return None
