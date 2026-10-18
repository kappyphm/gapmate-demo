# AGENTS.md

GapMate — CV ↔ JD analysis. Monorepo: React web + two FastAPI services + shared data.
Spec lives in `docs/` (read `03-data-contracts.md` and `04-scoring-ats-rules.md` before touching the pipeline).

## Run / verify

- Everything runs in Docker: `docker compose up --build`. Docker Desktop must be running (Windows).
- Copy `.env.example` → `.env` first (gitignored; never commit secrets — repo is public).
- Ports: web `5173`, core-api `8000`, analysis-api `8001`, postgres `5432`.
- Health: `curl localhost:8000/health`, `curl localhost:8001/health`. Swagger at `/docs` on both.
- analysis-api tests + lint (dev deps are not in the prod image):
  `docker compose exec analysis_api sh -c "pip install -q -r requirements-dev.txt && pytest -q && ruff check app tests && ruff format --check app tests"`.
- Web gates: `docker compose exec web sh -c "pnpm typecheck && pnpm build"`.
- Root `package.json` scripts (`pnpm up`, `pnpm down`, `pnpm dev:web`, `pnpm types:generate`) are conveniences only; there is **no root lockfile / no root install**.
- Web is the only Node package: install/deps live in `apps/web` (own `pnpm-lock.yaml`). Python services use plain `requirements.txt` (no lockfile).

## Hot reload & rebuild rules

- `./services/*` is bind-mounted to `/app` and run with `uvicorn --reload`, `./data` → `/data`. Local edits reload without rebuild.
- Rebuild only when `requirements.txt`, `Dockerfile`, or `docker-compose.yml` change.
- Web HMR relies on polling (`CHOKIDAR_USEPOLLING`, `server.watch.usePolling`) — keep it; native FS events don't work through the Windows bind mount.

## Service boundaries (do not cross)

- `analysis-api` is **stateless**: no DB, no user data, no persistence. It only reads `data/` (mounted at `/data`) and calls Gemini.
- `core-api` owns Postgres, auth, users, subscription/quota, history. It calls analysis-api over internal REST with `INTERNAL_API_KEY`.
- Never put Gemini calls or user models in core-api, and never add storage to analysis-api.

## Contract

- Pydantic models (in `core_api/app/schemas`) are the source of truth → OpenAPI → TS types.
- Generate web types with `pnpm types:generate` (core-api must be running). Web mirrors them with Zod.

## Quirks

- Web pins `"packageManager": "pnpm@9.12.2"`. Do not remove it: pnpm 10 fails with `ERR_PNPM_IGNORED_BUILDS` (esbuild postinstall).
- Many routes intentionally return `501` — this is the P0 scaffold. Implementation order is in `docs/06-roadmap-phases.md`.
- `data/skills-taxonomy.json`, `data/courses.json` hold canonical data; skill embeddings are precomputed at runtime and cached under `data/.cache/` (gitignored), not stored in the JSON.
- `data/samples/*` must stay synthetic (no PII) because the repo is public.

## Git workflow

- Trunk-based: `main` is stable; branch `feat/<scope>-<desc>` → squash-merge PR. Tag each phase `v0.x.0`.
- Conventional Commits; scopes: `web | core-api | analysis-api | infra | docs`.
- Pre-commit hooks (`.pre-commit-config.yaml`): `pip install pre-commit && pre-commit install`. CI is deferred (not present).
- On Windows/PowerShell, `git push` and `docker compose` write normal progress to stderr — red output ≠ failure; check `$LASTEXITCODE`.
