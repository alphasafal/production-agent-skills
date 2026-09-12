# Common Project Structure Cheat Sheet

Use this to orient quickly, then verify against actual code — these are
priors, not guarantees.

## Next.js
- `app/` (App Router) or `pages/` (Pages Router) — routing is file-based;
  `app/api/*/route.ts` or `pages/api/*.ts` are backend entry points inside
  a "frontend" repo.
- `middleware.ts` at root — runs before routing, common place for
  auth/redirect logic that's easy to miss when mapping data flow.
- `next.config.js` — check `rewrites`/`redirects`/`headers` for behavior
  that isn't visible in application code.

## Python service (Flask/FastAPI/Django)
- FastAPI/Flask: entry point is usually `main.py`/`app.py` or an
  `app factory` function; routes may be split across `routers/`/`blueprints/`.
- Django: `urls.py` per app plus a root `urls.py` including them;
  `settings.py` for config; `models.py` for persistence; check
  `MIDDLEWARE` list for cross-cutting request handling.
- Look for `alembic/` or Django `migrations/` for schema history.

## Go backend
- `cmd/<binary-name>/main.go` is the real entry point in idiomatic Go
  layouts; `internal/` holds code not meant to be imported by other
  modules (a real compiler-enforced boundary, not just convention).
- `pkg/` (if present) is the intended external-facing API surface.
- Routing often via `chi`, `gin`, `net/http` + a mux — check
  `go.mod` for which.

## Monorepo (generic)
- Look for `apps/` (deployables) vs. `packages/` or `libs/` (shared code) —
  a very common convention across Nx/Turborepo setups regardless of
  language.
- A root `README.md` or `docs/` often documents the intended dependency
  direction (apps depend on libs, never the reverse) — verify it's actually
  followed.

## General signals worth checking regardless of stack
- `Dockerfile`/`docker-compose.yml` — reveals actual runtime topology and
  service boundaries better than source layout alone.
- CI config (`.github/workflows/`, `.gitlab-ci.yml`) — reveals what's
  actually built/tested/deployed, which is sometimes narrower than what
  exists in the repo.
