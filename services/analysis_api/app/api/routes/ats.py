"""Standalone ATS check endpoint (P2).

Runs the deterministic rules engine (docs/04 Part C) on a parsed ``CVDoc`` plus layout facts,
optionally scoring keyword coverage against JD keywords.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.pipeline.ats import run_ats
from app.schemas.cv import CVDoc
from app.schemas.jd import JDDoc, Requirement
from app.schemas.report import AtsSection

router = APIRouter()


class AtsCheckRequest(BaseModel):
    cv: CVDoc
    cv_text: str = ""
    layout: dict = Field(default_factory=dict)
    jd_keywords: list[str] = Field(default_factory=list)


@router.post("/ats-check", response_model=AtsSection)
async def ats_check(payload: AtsCheckRequest) -> AtsSection:
    jd = JDDoc(
        keywords=payload.jd_keywords,
        requirements=[
            Requirement(raw=kw, skill_id=kw, importance=1.0, required=False)
            for kw in payload.jd_keywords
        ],
    )
    return run_ats(payload.cv, jd, text=payload.cv_text, layout=payload.layout)
