"""Parsed job description (see docs/03-data-contracts.md)."""

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    raw: str
    skill_id: str | None = None
    type: str = "hard"
    importance: float = 1.0
    required: bool = True
    level: int = 3
    category: str = ""


class JDDoc(BaseModel):
    language: str = "en"
    title: str = ""
    seniority: str = ""
    location: str = ""
    employment_type: str = ""
    requirements: list[Requirement] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
