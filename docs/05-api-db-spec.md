# 05 — API & Database Spec

## 1. core-api (public, JWT-protected except auth)

Base URL (dev): `http://localhost:8000`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | – | Liveness |
| POST | `/auth/google` | – | Exchange Google ID token → own JWT |
| POST | `/auth/refresh` | cookie | Rotate access token |
| GET | `/users/me` | JWT | Current user profile |
| GET | `/subscriptions` | JWT | List tiers |
| POST | `/subscriptions/checkout` | JWT | Stub checkout |
| POST | `/analyses` | JWT | Create analysis (orchestrates analysis-api) |
| GET | `/analyses` | JWT | List history (paginated) |
| GET | `/analyses/{id}` | JWT | Get one analysis |
| DELETE | `/analyses/{id}` | JWT | Delete analysis |

### `POST /auth/google`
```jsonc
// request
{ "id_token": "<google-id-token>" }
// response
{ "access_token": "<jwt>", "token_type": "bearer", "user": { "id": "", "email": "", "name": "" } }
```

### `POST /analyses`
```jsonc
// request
{ "cv": "<file or text>", "jd": "<text>", "options": { "role_template": "frontend", "hours_per_week": 8 } }
// response: Report (see 03-data-contracts) + { "id": "<analysis-id>" }
```

## 2. analysis-api (internal, `x-internal-key`)

Base URL (dev): `http://localhost:8001` — not exposed to the browser.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness |
| POST | `/v1/analyze` | Full pipeline → `Report` |
| POST | `/v1/parse/cv` | CV text → `CVDoc` |
| POST | `/v1/parse/jd` | JD text → `JDDoc` |
| POST | `/v1/ats-check` | `CVDoc` + layout → ATS section |
| POST | `/v1/recommend-courses` | gaps → ordered courses |
| GET | `/v1/taxonomy` | Skill taxonomy |
| GET | `/v1/courses` | Course catalog |

### `POST /v1/analyze`
```jsonc
// request
{ "cv_text": "", "jd_text": "", "cv_layout": {}, "options": { "role_template": "frontend", "hours_per_week": 8 } }
// response: Report (see 03-data-contracts) — includes `ats`, `suggestions`, `ats_preview`
```

### `POST /v1/ats-check`
```jsonc
// request
{ "cv": { /* CVDoc */ }, "cv_text": "", "layout": { /* extract layout facts */ }, "jd_keywords": ["typescript"] }
// response: AtsSection (score, issues[], keyword_coverage, format_issues)
```

> `cv_layout` / `layout` come from `POST /v1/extract` (file upload). When the CV is pasted as
> text, omit it and the engine assumes a single-column, text-based document.

## 3. Auth flow

```
Web: Google Identity Services → ID token
  → core-api POST /auth/google  (verify with Google JWKS)
  → upsert User → issue access JWT (15m) + refresh cookie (httpOnly, 7d)
Web: Authorization: Bearer <access>; on 401 → POST /auth/refresh
```

## 4. Database schema (PostgreSQL)

### `users`
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| google_sub | text unique | Google subject |
| email | text unique | |
| name | text | |
| avatar_url | text | |
| created_at | timestamptz | default now() |

### `subscriptions`
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| user_id | uuid FK users | |
| tier | text | free / pro |
| status | text | active / canceled |
| quota_limit | int | analyses per period |
| period_start | date | |
| period_end | date | |

### `analyses`
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| user_id | uuid FK users | |
| title | text | |
| cv_snapshot | text | encrypted at rest |
| jd_snapshot | text | |
| report_json | jsonb | full Report |
| overall_score | int | |
| ats_score | int | |
| pipeline_version | text | |
| created_at | timestamptz | |

### `usage_events`
| column | type | notes |
|---|---|---|
| id | uuid PK | |
| user_id | uuid FK users | |
| type | text | analyze |
| tokens | int | |
| cost_usd | numeric(10,4) | |
| created_at | timestamptz | |

## 5. Errors

Standard FastAPI error body:
```jsonc
{ "detail": "message" }
```
- `401` unauthenticated, `403` quota exceeded, `422` validation, `501` not implemented (scaffold).
