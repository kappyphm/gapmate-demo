# 01 — Product Requirements (PRD)

## 1. Product summary

**GapMate** is a CV ↔ JD analysis tool for job seekers. Given a CV and a target job
description, it produces an explainable report covering four areas:

1. **Match report & scoring** — how well the CV fits the JD, with a breakdown.
2. **ATS audit** — why the CV may be blocked by Applicant Tracking Systems, and how to fix it.
3. **Skill gap & roadmap** — what to learn next, prioritized.
4. **Course recommendations** — specific courses (from a catalog) mapped to the gaps.

**Positioning:** a *diagnostic, explainable* assistant. It is **not** an auto-writer that
fabricates experience.

## 2. Principles

1. **Explainable** — every score traces back to evidence in the CV/JD.
2. **Truthful** — never invent experience/skills; missing metrics become placeholders `[…]`.
3. **Stateless analysis** — the analysis engine holds no user data; persistence lives in core-api.
4. **Bilingual** — Vietnamese and English CVs/JDs, mixed allowed.

## 3. Personas

| Persona | Goal | Key outputs used |
|---|---|---|
| Minh — Fresher/Junior IT | Know if the CV passes ATS; what skills are missing | Match, ATS, Roadmap |
| Lan — Mid, job switching | Tailor CV to one specific JD; optimize keywords | Match, Suggestions |
| Hưng — Career switcher | A learning path from current skills to a target role | Gaps, Roadmap, Courses |

## 4. Core user journey

Login (Google) → New Analysis (upload CV + paste JD + options) → Report (4 tabs) →
apply a suggestion (before/after ATS) → saved to History → export PDF.

## 5. Functional requirements

### FR-1 Input
- FR-1.1 Upload CV as PDF or DOCX.
- FR-1.2 Paste or upload JD as text/PDF/DOCX.
- FR-1.3 Options: role template, available study hours/week.

### FR-2 Analysis (per run)
- FR-2.1 Parse CV into structured sections.
- FR-2.2 Parse JD into requirements (must-have / nice-to-have).
- FR-2.3 Produce overall match score + subscores (skills, experience, education, ATS keywords).
- FR-2.4 Produce ATS audit with issues, severity, and fixes.
- FR-2.5 Produce prioritized skill gaps.
- FR-2.6 Produce a learning roadmap in phases.
- FR-2.7 Recommend courses mapped to gaps and roadmap phases.
- FR-2.8 Produce concrete CV rewrite suggestions with rationale.

### FR-3 Report
- FR-3.1 Display all of the above in tabbed UI.
- FR-3.2 Show evidence for each match/gap.
- FR-3.3 Show before/after ATS score when suggestions are applied.
- FR-3.4 Export report as PDF.

### FR-4 Accounts & history
- FR-4.1 Sign in with Google.
- FR-4.2 Persist analysis history per user.
- FR-4.3 Free/Pro tiers with usage quota.

## 6. Non-functional requirements

| Area | Requirement |
|---|---|
| Latency | Synchronous analysis; target ≤ 60s (parallelize stages) |
| Privacy | CV is PII: encrypt at rest, never log content, support delete |
| Cost | Track tokens/cost per analysis (UsageEvent) |
| Explainability | Confidence reported alongside scores |
| i18n | Vietnamese + English |

## 7. Out of scope (demo)

- Recruiter-side ranking of many candidates.
- Automated job applications.
- Payments/billing provider integration (stubbed).
- Non-IT role templates at launch (IT only).

## 8. Acceptance criteria (demo)

- A user can sign in, submit a CV + JD, and receive a report with all 4 sections.
- Applying suggestions recomputes and shows an increased ATS score.
- History persists and can be reopened and deleted.
- The report exports to PDF.
- The pipeline is stateless: `analysis-api` stores nothing.

## 9. Success metrics (demo)

- % users who apply ≥ 1 suggestion and see ATS score improve.
- Time to first report.
- Report confidence ≥ threshold on the golden dataset.
