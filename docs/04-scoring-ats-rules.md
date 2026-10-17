# 04 — Scoring Rubric & ATS Ruleset

## Part A — Matching engine

Requirements (from `JDDoc.requirements`) are matched against `CVDoc.skills` in a cascade.
Every match records `match_type` and `evidence_span` for explainability.

| Step | Condition | `match_score` |
|---|---|---|
| B1 exact | normalized `skill_id` equal | 1.00 |
| B2 alias/related | alias hit, or a `related` skill present | 0.85–0.90 |
| B3 embedding | `cos(req_emb, cv_emb) > T_high` | 0.70–0.90 (scaled by cosine) |
| B4 LLM adjudication | `T_mid < cos ≤ T_high` or ambiguous level | 0.50–0.85 (LLM verdict) |
| B5 miss | none | 0.00 |

Default thresholds: `T_high = 0.82`, `T_mid = 0.70` (tuned on the golden set).

**Level factor** applied when the JD requests a proficiency level:
```
level_factor = 1                                  if cv_level >= req_level
             = 0.6 + 0.4 * (cv_level / req_level)  otherwise
final_i = match_score * level_factor
```

## Part B — Scoring rubric

```
Overall = Σ w_k · S_k
```

Default weights (role template can override):

| Subscore | Weight | Formula |
|---|---|---|
| Skills | 0.40 | `100 · Σ(importance_i · final_i) / Σ importance_i` |
| Experience | 0.30 | `0.40·min(years_relevant/required,1) + 0.35·relevance_sim + 0.25·seniority_fit` |
| Education | 0.15 | `0.60·degree_level_fit + 0.25·field_relevance + 0.15·certs_bonus` |
| ATS keywords | 0.15 | weighted pass of the ATS rule set (Part C) |

**Must-have penalty:** if any required requirement is missing → `S_skills *= 0.85`.

- `years_relevant`: sum of experience durations whose skills overlap the JD.
- `relevance_sim`: cosine between embeddings of recent roles' text and the JD.
- `seniority_fit`: 1.0 if CV seniority ≥ JD seniority, else scaled down.
- `degree_level_fit`: map (none<bachelor<master<phd) to CV vs JD requirement.

**Confidence** = `f(parse_confidence, rule_share)` where `rule_share` is the fraction of
matches decided by rules/alias vs LLM. Report as `overall ± delta`.

## Part C — ATS ruleset

Each rule returns `{ code, severity, weight, pass, message, fix }`.
ATS score = `100 · Σ(weight · pass) / Σ weight`.

### Group A — Parseability (layout-aware, PyMuPDF)

| Code | Check | Severity |
|---|---|---|
| A1 | Supported file type (PDF/DOCX) | critical |
| A2 | Extractable text (not a scanned image) | critical |
| A3 | Single-column layout | critical |
| A4 | No tables used for layout | warn |
| A5 | No critical content in header/footer | warn |
| A6 | Contact info not embedded in images/icon fonts | warn |
| A7 | Standard fonts | info |
| A8 | No content in text boxes | info |

> If A2 fails, run OCR (Tesseract vie+eng) — the audit then flags "scanned CV" as an issue.

### Group B — Structure

| Code | Check | Severity |
|---|---|---|
| B1 | Standard section headings present (Summary/Experience/Education/Skills) | warn |
| B2 | Consistent date format (MM/YYYY) | warn |
| B3 | Email + phone (+ LinkedIn) present | critical |
| B4 | Clear job title | warn |
| B5 | Uses bullet points | info |
| B6 | Length 1–2 pages | info |

### Group C — Content / keywords

| Code | Check | Severity |
|---|---|---|
| C1 | Keyword coverage vs JD | warn |
| C2 | Keyword density not stuffed | warn |
| C3 | Action verbs used | info |
| C4 | Quantified achievements present | info |
| C5 | Acronym + full form both present (e.g., "JavaScript (JS)") | info |
| C6 | No spelling/grammar errors | info |

`keyword_coverage` lists JD keywords present/missing in the CV → feeds the Suggestions stage.

## Part D — Gap priority

```
gap_severity = importance_jd · (1 - final_i) · (required ? 1.0 : 0.6)
priority     = normalize(gap_severity) bucketed into P0 / P1 / P2
```

- **P0 Must-close** — required, high importance.
- **P1 Nice-to-have.**
- **P2 Already strong** (for encouragement).

**Learning adjacency:** if the candidate already has a `related` skill, mark `adjacent_to` and
move the gap earlier in the roadmap (fast wins first).

## Part E — Suggestions

For each weak bullet / missing section, return:
`{ section, original, improved, reason, jd_keywords_addressed, needs_user_input }`.

Guardrails:
- Never invent experience or skills.
- Insert metric placeholders `[…]` where numbers are missing (`needs_user_input`).
- Prefer embedding JD keywords naturally.

**Before/After ATS:** re-run the ATS ruleset on the accepted edits and show `before → after`.
