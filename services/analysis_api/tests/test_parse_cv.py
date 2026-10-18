"""Heuristic CV parser: experience is structured and education is not experience."""

import pytest

from app.core.config import settings
from app.pipeline.parse_cv import parse_cv

CV = """# Jane Doe
- Email: jane@example.com
- Phone: 0900000000

## Summary
Frontend developer.

## Experience
### Acme Corp — Senior Frontend Developer (06/2022 – Present)
- Built the design system with React.
- Led a team of 4 engineers.

### Beta Studio — Frontend Developer (01/2020 – 05/2022)
- Shipped the marketing site.

## Education
- Some University — B.Sc. Computer Science (2014 – 2018)
"""


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")


def test_experience_roles_titles_and_bullets():
    cv = parse_cv(CV)
    titles = [e.title for e in cv.experience]
    assert "Senior Frontend Developer" in titles
    assert "Frontend Developer" in titles
    first = cv.experience[0]
    assert first.company == "Acme Corp"
    assert "Built the design system with React." in first.bullets


def test_education_years_are_not_experience():
    cv = parse_cv(CV)
    assert len(cv.experience) == 2
    assert all(e.start != "2014" for e in cv.experience)
