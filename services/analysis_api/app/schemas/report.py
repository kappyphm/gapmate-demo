"""Analysis request/response contracts (see docs/03-data-contracts.md)."""

from pydantic import BaseModel, Field


class AnalyzeOptions(BaseModel):
    role_template: str = "frontend"
    hours_per_week: int = 8


class AnalyzeRequest(BaseModel):
    cv_text: str = ""
    jd_text: str = ""
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)


class MatchSubscores(BaseModel):
    skills: float = 0.0
    experience: float = 0.0
    education: float = 0.0
    keywords: float = 0.0


class MatchedItem(BaseModel):
    skill_id: str
    match_score: float
    match_type: str
    evidence_span: str = ""


class MissingItem(BaseModel):
    skill_id: str
    required: bool
    importance: float


class MatchResult(BaseModel):
    overall: int = 0
    subscores: MatchSubscores = Field(default_factory=MatchSubscores)
    matched: list[MatchedItem] = Field(default_factory=list)
    missing: list[MissingItem] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class ReportMeta(BaseModel):
    pipeline_version: str
    created_at: str
    confidence: float = 0.0
    mode: str = "heuristic"
    role_template: str = "frontend"


class Report(BaseModel):
    meta: ReportMeta
    match: MatchResult
    ats: dict | None = None
    gaps: list[dict] = Field(default_factory=list)
    roadmap: list[dict] = Field(default_factory=list)
    courses: list[dict] = Field(default_factory=list)
    suggestions: list[dict] = Field(default_factory=list)
