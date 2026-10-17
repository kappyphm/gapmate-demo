"""Analysis request schemas (mirror of analysis-api contract)."""

from pydantic import BaseModel, Field


class AnalyzeOptions(BaseModel):
    role_template: str = "frontend"
    hours_per_week: int = 8


class AnalyzeRequest(BaseModel):
    cv_text: str = ""
    jd_text: str = ""
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)
