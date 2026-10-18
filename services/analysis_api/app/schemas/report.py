"""Analysis request/response contracts (see docs/03-data-contracts.md)."""

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeOptions(BaseModel):
    role_template: str = "frontend"
    hours_per_week: int = 8


class AnalyzeRequest(BaseModel):
    cv_text: str = ""
    jd_text: str = ""
    cv_layout: dict = Field(default_factory=dict)
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


class AtsIssue(BaseModel):
    """One rule outcome (docs/04 Part C)."""

    model_config = ConfigDict(populate_by_name=True)

    code: str
    severity: str = "info"
    weight: int = 1
    passed: bool = Field(default=True, alias="pass")
    message: str = ""
    fix: str = ""


class KeywordCoverage(BaseModel):
    matched: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class AtsSection(BaseModel):
    score: int = 0
    issues: list[AtsIssue] = Field(default_factory=list)
    keyword_coverage: KeywordCoverage = Field(default_factory=KeywordCoverage)
    format_issues: list[str] = Field(default_factory=list)
    projected_score: int | None = None


class SuggestionItem(BaseModel):
    section: str
    original: str = ""
    improved: str = ""
    reason: str = ""
    jd_keywords_addressed: list[str] = Field(default_factory=list)
    needs_user_input: list[str] = Field(default_factory=list)
    code: str = ""


class AtsPreview(BaseModel):
    before: int = 0
    after: int = 0


class ReportMeta(BaseModel):
    pipeline_version: str
    created_at: str
    confidence: float = 0.0
    mode: str = "heuristic"
    role_template: str = "frontend"


class Report(BaseModel):
    meta: ReportMeta
    match: MatchResult
    ats: AtsSection | None = None
    gaps: list[dict] = Field(default_factory=list)
    roadmap: list[dict] = Field(default_factory=list)
    courses: list[dict] = Field(default_factory=list)
    suggestions: list[SuggestionItem] = Field(default_factory=list)
    ats_preview: AtsPreview | None = None
