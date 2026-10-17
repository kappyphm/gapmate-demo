# GapMate

CV ↔ JD analysis engine for job seekers: **match scoring**, **ATS audit**, **skill-gap roadmap**, and **course recommendations**.

> Diagnostic and explainable — every score traces back to evidence in the CV/JD. The analysis engine never fabricates experience.

## Architecture

```
[Web SPA (Vite/React)] ──HTTPS+JWT──▶ [core-api (FastAPI)]  ──▶ Postgres
                                            │ internal REST (x-internal-key)
                                            ▼
                                     [analysis-api (FastAPI)] ──▶ Gemini (flash + embeddings)
                                            └─ reads data/ (taxonomy, courses)
```

- `apps/web` — React SPA (UI only).
- `services/core_api` — SaaS platform: auth (Google OAuth), users, subscription, quota, history, orchestrator.
- `services/analysis_api` — stateless analysis pipeline.
- `data/` — skill taxonomy, course catalog, sample CVs/JDs.

See [`docs/`](./docs) for the full specification.

## Quick start

```bash
cp .env.example .env      # fill GEMINI_API_KEY + GOOGLE_CLIENT_ID/SECRET
docker compose up --build
```

| Service | URL |
|---|---|
| Web | http://localhost:5173 |
| core-api | http://localhost:8000/docs |
| analysis-api | http://localhost:8001/docs |

## Development

- Everything runs in Docker (web uses volume mount + polling for HMR).
- Git: trunk-based, Conventional Commits. See [`docs/06-roadmap-phases.md`](./docs/06-roadmap-phases.md).

## Docs

| File | Nội dung |
|---|---|
| `docs/01-PRD.md` | Product requirements |
| `docs/02-architecture.md` | Architecture & pipeline |
| `docs/03-data-contracts.md` | Data schemas |
| `docs/04-scoring-ats-rules.md` | Scoring rubric & ATS rules |
| `docs/05-api-db-spec.md` | API & DB spec |
| `docs/06-roadmap-phases.md` | Roadmap & git workflow |
