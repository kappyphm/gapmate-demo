# 06 — Roadmap & Git Workflow

## 1. Phases

| Phase | Deliverable | Demoable outcome | Git |
|---|---|---|---|
| **P0** | Monorepo scaffold, docker-compose (postgres + 2 api + web), `.env.example`, sample data, 6 docs, git setup + GitHub repo | `docker compose up` runs the skeleton | init `main`, first commit |
| **P1** | analysis-api: `extract → parse_cv → parse_jd → normalize → match → score`; web Report (Match tab) | Upload CV/JD → match score + breakdown | `feat/p1-*` → tag `v0.1.0` |
| **P2** | ATS rules engine + Suggestions (before/after score) | ATS audit + rewrite suggestions | tag `v0.2.0` |
| **P3** | Gap prioritizer + Roadmap + Course recommender | Roadmap + course list | tag `v0.3.0` |
| **P4** | core-api: Google OAuth + JWT + history + quota; web login/dashboard/history | Login + saved history | tag `v0.4.0` |
| **P5** | Export PDF, streaming UX, polish, demo script, README | Complete demo | tag `v0.5.0` |

## 2. Definition of done (per phase)

- Code runs via `docker compose up`.
- Ruff clean (services), typecheck/build clean (web).
- New endpoints documented in `docs/`.
- Golden-set regression still within expected score ranges (from P2).

## 3. Git workflow

**Model:** trunk-based.

- `main` is the stable branch and is **protected** (no direct push; merge via PR).
- Short-lived branches: `feat/<scope>-<desc>`, `fix/<scope>-<desc>`, `docs/<desc>`.
- Merge via **squash merge** into `main`.
- Tag each phase: `v0.1.0`, `v0.2.0`, …

**Commit convention:** Conventional Commits.
```
<type>(<scope>): <description>

feat(analysis-api): implement skill matcher cascade
fix(web): correct ATS before/after recalculation
docs: add data contract for Report
```
Types: `feat|fix|chore|docs|refactor|test|build|ci`.
Scopes: `web|core-api|analysis-api|infra|docs`.

## 4. Repository setup

```bash
git init -b main
# .gitignore, .gitattributes, .pre-commit-config.yaml already present
pip install pre-commit && pre-commit install
gh repo create gapmate-demo --public --source . --remote origin
git add . && git commit -m "chore(infra): scaffold GapMate monorepo (P0)"
git push -u origin main
```

- Remote: **GitHub public** (`gapmate-demo`).
- `.env` is never committed; only `.env.example`.
- Repo is public → use **synthetic** CV/JD samples (already the case in `data/samples/`).

## 5. Hooks (pre-commit)

Configured in `.pre-commit-config.yaml`:
trailing-whitespace, end-of-file-fixer, check-yaml/json/toml, check-merge-conflict,
check-added-large-files, detect-private-key, ruff (lint+format), prettier.

> CI (GitHub Actions) is intentionally deferred to a later phase.

## 6. Demo script

> Persona: **Minh — junior frontend applying for a React role.**

1. Sign in with Google.
2. New Analysis → upload `data/samples/cv_vi.md` + paste `data/samples/jd_frontend.md`.
3. Show **Overall 64** (± confidence) and subscores.
4. Open **ATS** tab → 2 critical issues (multi-column, missing keywords).
5. Apply 3 suggestions → ATS **58 → 81**.
6. Open **Roadmap** tab → 90-day plan covering TypeScript / Testing.
7. Open **Courses** tab → 4 courses mapped to gaps.
8. Finish at **History** → reopen and export PDF.

## 7. Known risks

| Risk | Mitigation |
|---|---|
| PDF layout loss → weak ATS group A | PyMuPDF layout + OCR fallback |
| Free-form Vietnamese CVs without headings | LLM parse + heuristics |
| LLM score variance | `responseSchema` + fixed rubric + golden set |
| Cost/latency | cache embeddings + parallel stages + small model for parsing |
| Taxonomy coverage gaps | seed IT first; fallback via embedding + LLM |
