# 02 — Architecture

## 1. Overview

GapMate is a SaaS-ready monorepo with a hard boundary between the **analysis engine**
(stateless) and the **SaaS platform** (users, subscriptions, history).

```
┌─────────────────┐   HTTPS + JWT   ┌──────────────────────────────┐
│  apps/web       │ ──────────────▶ │  services/core_api           │
│  Vite + React   │                 │  • Auth (Google OAuth)       │
│  UI only        │ ◀────────────── │  • Users / Subscription      │
└─────────────────┘                 │  • Quota / Metering          │
                                    │  • Analysis history (DB)     │
                                    │  • Orchestrator              │
                                    └───────────┬──────────────────┘
                                                │ internal REST (x-internal-key)
                                                ▼
                                    ┌──────────────────────────────┐
                                    │  services/analysis_api       │
                                    │  STATELESS — no user data    │
                                    │  pipeline: parse→match→…     │
                                    └───────────┬──────────────────┘
                                                │
                                          Gemini (flash + embeddings)
                                    ┌──────────────────────────────┐
                                    │  PostgreSQL 16               │
                                    │  (only core_api accesses)    │
                                    └──────────────────────────────┘
```

## 2. Why split the services

- **analysis_api** is stateless and LLM/CPU heavy → scale horizontally, swap models,
  version the pipeline without touching SaaS logic.
- **core_api** owns all SaaS concerns (tiers, quota, billing) → the part that grows "later".
- Contract is a shared JSON schema (Pydantic → OpenAPI → TS) so either side can move to its
  own repo/service with no client change.

## 3. Repository layout

```
gapmate-demo/
├─ apps/web/                       # Vite React SPA
├─ services/core_api/app/          # FastAPI SaaS platform
├─ services/analysis_api/app/      # FastAPI pipeline
├─ packages/shared-types/          # TS types generated from OpenAPI
├─ data/                           # taxonomy, course catalog, samples
├─ docs/
├─ docker-compose.yml
├─ .env.example
└─ README.md
```

## 4. Analysis pipeline (analysis_api)

Each stage is a pure function with explicit input/output schemas (testable in isolation).

| # | Stage | Input | Output | Tech |
|---|---|---|---|---|
| 1 | `extract` | file bytes | text + layout blocks | PyMuPDF, python-docx, OCR fallback |
| 2 | `parse_cv` | text + layout | `CVDoc` | Gemini structured + regex |
| 3 | `parse_jd` | text | `JDDoc` | Gemini structured + rules |
| 4 | `normalize` | raw skills | skill ids, levels, evidence | taxonomy + embedding fallback |
| 5 | `match` | CVDoc + JDDoc | `MatchResult` | rule → embedding → LLM adjudication |
| 6 | `score` | MatchResult | subscores + overall + confidence | rubric |
| 7 | `ats` | CVDoc + layout | issues + ATS score | rules engine |
| 8 | `gap` | match + jd | prioritized gaps | priority formula |
| 9 | `suggest` | CVDoc + gaps + jd | rewrites | constrained LLM |
| 10 | `roadmap` | gaps + time option | phases | LLM + ordering heuristic |
| 11 | `recommend` | gaps + catalog | ordered courses | deterministic + LLM rerank |

Stages 2/3/7 can run in parallel; 8–11 depend on 5/6/7.

## 5. External dependencies

- **Gemini** — `gemini-3.5-flash-lite` for parsing/reasoning, `gemini-embedding-001` for semantic match.
  Set `GEMINI_API_KEY`. Structured output (`responseSchema`) is required for parsers/scores.
- **PostgreSQL 16** — accessed only by core_api via SQLAlchemy async + Alembic.
- **Tesseract OCR** (vie+eng) installed in the analysis_api image for scanned PDFs.

## 6. Deployment

- **Dev/demo:** everything via `docker compose up` (web HMR over volume mount + polling).
- **Prod (future):** web on a static host/CDN; core_api + analysis_api as separate services;
  Postgres managed; analysis_api scaled horizontally (stateless).

## 7. Security

- JWT (access 15m + refresh httpOnly 7d) issued by core_api.
- `INTERNAL_API_KEY` guards core_api → analysis_api calls.
- PII: no CV content in logs; encryption at rest; data-deletion endpoint.
- CORS restricted to the web origin.
