# 07 — Analysis Pipeline

How the CV/JD analysis flow is built. This document defines **how** the pipeline in
[`02-architecture.md`](./02-architecture.md) is implemented; it does not change the product
philosophy in [`01-PRD.md`](./01-PRD.md) or the rules in [`04-scoring-ats-rules.md`](./04-scoring-ats-rules.md).

## 1. Design principles

1. **Facts are deterministic; AI provides decision support.**
   Extraction, normalization, matching, scoring and gap priority are deterministic rules.
   AI is only used where judgment is needed (parsing free-form text, adjudicating ambiguous
   matches, roadmaps) and never for factual matching that a rule can decide.
2. **Explainable** — every score traces back to an `evidence_span` in the CV/JD
   ([`01-PRD.md`](./01-PRD.md) §2).
3. **Truthful / no fabrication** — the engine never invents experience or skills; missing
   metrics become placeholders `[…]`.
4. **AI is validated before use** — AI output is parsed as JSON and checked by local business
   validators. If AI is unavailable or fails validation, the pipeline **falls back to the
   deterministic result**; it never blocks a request.
5. **Stateless** — the pipeline holds no user data; persistence lives in core-api.

> **Inherited vs. kept.** The robustness *patterns* (alias matching, candidate discovery,
> evidence excerpts, AI output validators, rule-based fallback) are adapted from the FitGap
> reference project (see Appendix). The GapMate *design* is preserved: the matching cascade in
> [`04-scoring-ats-rules.md`](./04-scoring-ats-rules.md) Part A (embedding + LLM adjudication)
> and the deterministic gap-priority formula (Part D) stay as specified. FitGap does *not* have
> those; copying FitGap verbatim would be a downgrade.

## 2. Pipeline overview

11 stages, each a pure function with explicit input/output schemas (testable in isolation).
Stages 2/3/7 can run in parallel; 8–11 depend on 5/6/7.

| # | Stage | Deterministic / AI | Module |
|---|---|---|---|
| 1 | `extract` | deterministic (+ OCR fallback) | `app/pipeline/extract.py` |
| 2 | `parse_cv` | AI structured + heuristic fallback | `app/pipeline/parse_cv.py` |
| 3 | `parse_jd` | AI structured + heuristic fallback | `app/pipeline/parse_jd.py` |
| 4 | `normalize` | deterministic | `app/pipeline/normalize.py`, `app/data_loader.py` |
| 5 | `match` | cascade: rule → embedding → AI adjudication | `app/pipeline/match.py` |
| 6 | `score` | deterministic | `app/pipeline/score.py` |
| 7 | `ats` | deterministic rules | `app/pipeline/ats.py` |
| 8 | `gap` | deterministic (AI may re-rank/explain) | `app/pipeline/gap.py` |
| 9 | `suggest` | constrained AI | `app/pipeline/suggest.py` |
| 10 | `roadmap` | AI + ordering heuristic + rule fallback | `app/pipeline/roadmap.py` |
| 11 | `recommend` | deterministic + AI rerank | `app/pipeline/recommend.py` |

The orchestrator is `app/pipeline/analyze.py`, exposed by `POST /v1/analyze`.

## 3. Mapping: FitGap reference → GapMate pipeline

| FitGap module | GapMate stage | What to adapt |
|---|---|---|
| `document_extraction.py` | 1 `extract` | upload validation + OCR fallback |
| `skill_catalogue.py` | 4 `normalize` | canonical skills + aliases + category/source |
| `skill_candidates.py` | 4 `normalize` | conservative discovery of out-of-taxonomy skills |
| `skill_normalisation.py` | 4 `normalize` | stable `normalise_skill_key` comparison key |
| `services.extract_skills` / `compare_skills` | 4/5 | alias-pattern matching + set comparison |
| `services.calculate_match_score` | 6 `score` | share-of-required-skills scoring |
| `services.build_skill_evidence_details` | 5/6 | two-sided evidence + highlight parts |
| `ai_prioritisation.py` | 8 `gap` | AI re-rank on verified gaps only (optional) |
| `ai_learning_roadmap.py` | 10 `roadmap` | nested schema + per-field validator |
| `RECOMMENDATION_CATALOGUE` | 11 `recommend` | rule-based fallback when AI is unavailable |

## 4. Stage details

### Stage 1 — `extract`
Input: file bytes + filename. Output: `text` + basic `layout` blocks.

- Validate: supported type (PDF/DOCX/TXT), size limit (≤ 5 MB), reject empty/corrupt/password-protected.
- PDF via PyMuPDF; DOCX via `python-docx`.
- **OCR fallback** (Tesseract `vie+eng`, already installed in the analysis_api image) when no
  extractable text is found — feeds the ATS Group A rules (see [`04`](./04-scoring-ats-rules.md) Part C).

### Stage 2/3 — `parse_cv` / `parse_jd`
Input: text (+ layout for CV). Output: `CVDoc` / `JDDoc` ([`03-data-contracts.md`](./03-data-contracts.md)).

- Primary: Gemini structured output (`responseSchema`).
- Fallback: heuristic/regex parser.
- Each recognized skill/requirement carries `evidence_span`; the CV and JD sides each keep
  evidence occurrences with `highlight_parts` (matched term + `is_alias`).

### Stage 4 — `normalize`
Input: raw skill mentions. Output: taxonomy `skill_id` + level + evidence.

- Taxonomy + alias index (`data/skills-taxonomy.json`).
- Alias matching uses a **word-boundary, space/hyphen-flexible** pattern so aliases never match
  inside longer words (e.g. `git` ≠ `digital`).
- **Candidate discovery**: conservatively surface skill-like phrases not in the taxonomy
  (acronyms, method phrases) with a stop-term filter, so cross-domain skills are not dropped.
- Embeddings are computed at runtime and cached under `data/.cache/` (gitignored), not stored in JSON.

### Stage 5 — `match`
Cascade from [`04`](./04-scoring-ats-rules.md) Part A. Each match records `match_type` and `evidence_span`.

| Step | Condition | `match_score` |
|---|---|---|
| B1 exact | normalized `skill_id` equal (aliases resolve here) | 1.00 |
| B2 alias | alias hit — already normalized to the same `skill_id` | 1.00 |
| B3 embedding | `cos(req_emb, cv_emb) > T_high` | 0.70–0.90 (scaled) |
| B4 LLM adjudication | `T_mid < cos ≤ T_high` or ambiguous level | 0.50–0.85 (verdict) |
| B5 miss | none | 0.00 |

`related` skills are **not** matches (they feed gap adjacency). ATS `keyword_coverage` is fed the
same matched set, so a skill cannot be reported as both matched and missing.

Level factor is applied per [`04`](./04-scoring-ats-rules.md) Part A. Thresholds `T_high = 0.95`,
`T_mid = 0.88`, tuned on the golden set (high because `gemini-embedding-001` similarity baseline is
high; the middle band defers to LLM adjudication).

### Stage 6 — `score`
Rubric from [`04`](./04-scoring-ats-rules.md) Part B: weighted subscores (skills 0.40,
experience 0.30, education 0.15, keywords 0.15), must-have penalty `×0.85`, and
`confidence = f(parse_confidence, rule_share)` where `rule_share` is the fraction of matches
decided by rules/alias vs. LLM.

### Stage 7 — `ats`
Ruleset from [`04`](./04-scoring-ats-rules.md) Part C. Each rule returns
`{ code, severity, weight, pass, message, fix }`; ATS score = `100 · Σ(weight·pass) / Σ weight`.
`keyword_coverage` feeds Stage 9 (Suggestions).

### Stage 8 — `gap`
Deterministic priority formula from [`04`](./04-scoring-ats-rules.md) Part D:
`gap_severity = importance_jd · (1 - final_i) · (required ? 1.0 : 0.6)`, bucketed into P0/P1/P2,
with **learning adjacency** (`adjacent_to`) to surface fast wins first.

- AI is **optional and additive**: it may re-rank or explain **only the already-verified missing
  skills**. Its output is validated back against the verified set (mirroring FitGap's
  `validate_ai_priorities`); any mismatch → keep the deterministic order.

### Stage 9 — `suggest`
Constrained LLM rewriting of weak bullets/sections :
`{ section, original, improved, reason, jd_keywords_addressed, needs_user_input }`.
Guardrails: never invent experience or skills; insert `[…]` where metrics are missing; improve
existing content only. Missing JD skills are handled by Stage 8 (gap), not rewritten into the CV.
Re-running the ATS ruleset on the accepted edits yields `before → after`.

### Stage 10 — `roadmap`
Ordered phases building on Stage 8 gaps, with an AI-generated plan validated by a **nested schema
+ per-field validator** (mirroring FitGap's `validate_learning_roadmap`).
Fallback when AI is unavailable: rule-based recommendations.

### Stage 11 — `recommend`
Deterministic match of gaps → `data/courses.json` (skill overlap, level, language), optionally
re-ranked by AI. Replace the current `501` stub in `app/api/routes/courses.py`.

## 5. AI guardrails (Gemini)

Applies to every AI call (`app/llm/gemini.py`).

- **Bounded request**: explicit timeout, no automatic retries (`max_retries = 0`), non-streaming,
  JSON/schema mode.
- **Validate locally**: parse JSON → run business validator → use; otherwise fall back.
- **Graceful degradation**: any failure returns `None`/raises a typed *Unavailable* error so the
  caller keeps the deterministic result. Requests never fail because AI failed.
- **Safe logging**: log a category only (`timeout | api_exception | json_parsing | validation`),
  never provider payloads or CV/JD content.
- **Embeddings**: `gemini-embedding-001`, cached under `data/.cache/`.

## 6. Low-coverage path

When no structured JD skills are recognized (`parse_confidence` low / empty `JDDoc.requirements`),
the pipeline enters a **low-coverage** mode instead of reporting a genuine zero match.

- Deterministic output stays as-is.
- AI may suggest candidate learning priorities, explicitly labelled **AI-suggested**, and must not
  claim any skill was deterministically matched or missing.
- The low-coverage suggestions never overwrite deterministic results.

## 7. Testing strategy

- AI calls are tested with SDK mocks / a local HTTP mock transport — no real API key or network
  required (mirrors FitGap's 69 AI/boundary tests).
- Unit-test every stage as a pure function; add boundary tests for every AI validator
  (wrong type, missing field, over-limit, unknown skill, duplicate, invalid enum).
- Golden-set regression: overall scores stay within the expected ranges from P2.

## 8. Phase alignment

Per [`06-roadmap-phases.md`](./06-roadmap-phases.md):

| Phase | Pipeline work |
|---|---|
| **P1** ✅ | Stages 1–6 skeleton: `extract → parse → normalize → match → score` (B1–B2 only) |
| **P2** ✅ | Stage 7 `ats` (rules engine); `extract` hardening (validation + OCR + layout facts); B3 embedding / B4 LLM adjudication; Stage 9 `suggest` (deterministic subset + before/after ATS projection) |
| **P3** | Stages 8–11 `gap / roadmap / recommend` (+ candidate discovery) |
| **P5** | Stage 9 full LLM rewriter, streaming UX |

## Appendix — FitGap reference files

Reference project: `zhouzhengqin2024/FitGap` (`analysis/`).

| Pattern | FitGap file |
|---|---|
| Upload validation + extraction | `document_extraction.py` |
| Alias-pattern matching | `services.py` (`_build_alias_pattern`) |
| Canonical skills + aliases | `skill_catalogue.py` |
| Out-of-taxonomy discovery | `skill_candidates.py` |
| Comparison key | `skill_normalisation.py` |
| Two-sided evidence | `services.py` (`build_skill_evidence_details`) |
| AI gap re-ranking + validation | `ai_prioritisation.py` |
| AI roadmap + nested validator | `ai_learning_roadmap.py` |
| Rule-based recommendation fallback | `services.py` (`RECOMMENDATION_CATALOGUE`) |
