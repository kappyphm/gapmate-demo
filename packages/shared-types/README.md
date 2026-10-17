# @gapmate/shared-types

Single source of truth for the web ⇄ core-api contract.

- Pydantic models in `services/core_api/app/schemas` generate the OpenAPI schema.
- `src/api.d.ts` is generated from that schema with `openapi-typescript`.

## Generate

```bash
# core-api must be running (docker compose up core_api)
pnpm --filter @gapmate/shared-types generate
```
