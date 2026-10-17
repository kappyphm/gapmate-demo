"""Parsed CV document (see docs/03-data-contracts.md)."""

from pydantic import BaseModel, Field


class Contact(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""


class SkillItem(BaseModel):
    raw: str
    skill_id: str | None = None
    level: int = 3
    evidence_span: str = ""


class ExperienceItem(BaseModel):
    company: str = ""
    title: str = ""
    start: str = ""
    end: str = ""
    location: str = ""
    seniority: str = ""
    bullets: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    start: str = ""
    end: str = ""
    gpa: str = ""


class CVDocMeta(BaseModel):
    pages: int = 1
    parse_confidence: float = 0.0


class CVDoc(BaseModel):
    language: str = "en"
    contact: Contact = Field(default_factory=Contact)
    summary: str = ""
    skills: list[SkillItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    meta: CVDocMeta = Field(default_factory=CVDocMeta)
