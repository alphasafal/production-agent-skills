# Common Project Structure Cheat Sheet

Use this to orient quickly, then verify against actual code — these are
priors, not guarantees.

## First: is this an application or a library?

This changes what "entry point" even means, and getting it wrong sends the
whole map in the wrong direction:

- **Application/service**: execution starts somewhere (a `main`, a served
  route, a CLI command, a worker loop). Map the request/job flow.
- **Library/framework**: nothing "starts" — the entry point is the
  **exported public API surface**, and its consumers are external code you
  can't see. Map what's exported and what's deliberately internal instead
  of hunting for a `main` that doesn't exist.

Signals it's a library: no `Dockerfile`/deploy config, no server bootstrap,
a populated `exports`/`files`/`__all__`/exported-identifier surface, and
packaging metadata aimed at publishing (`pyproject.toml` with a build
backend, `package.json` with `files`, a Go module with no `cmd/`).

## Next.js
- `app/` (App Router) or `pages/` (Pages Router) — routing is file-based;
  `app/api/*/route.ts` or `pages/api/*.ts` are backend entry points inside
  a "frontend" repo.
- `middleware.ts` at root — runs before routing, common place for
  auth/redirect logic that's easy to miss when mapping data flow.
- `next.config.js` — check `rewrites`/`redirects`/`headers` for behavior
  that isn't visible in application code.

## Python
- **`src/` layout**: a very common packaging convention (Flask itself uses
  `src/flask/`). The importable package is `src/<name>/`, *not* the repo
  root — mapping the root as if it were the package produces a wrong module
  map. Confirm against `pyproject.toml` (`tool.setuptools`/`hatch` package
  discovery, or a `source = ["src", ...]` coverage setting).
- **Library**: `__init__.py`'s imports and `__all__` define the public API
  surface — that's the entry point to map.
- FastAPI/Flask **service**: entry point is usually `main.py`/`app.py` or an
  `app factory` function; routes may be split across `routers/`/`blueprints/`.
- Django: `urls.py` per app plus a root `urls.py` including them;
  `settings.py` for config; `models.py` for persistence; check
  `MIDDLEWARE` list for cross-cutting request handling.
- Look for `alembic/` or Django `migrations/` for schema history.

## Go
- **Service**: `cmd/<binary-name>/main.go` is the real entry point in
  idiomatic layouts; routing often via `chi`, `gin`, or `net/http` + a
  mux — check `go.mod` for which.
- **Library**: there is usually **no `cmd/`** at all (e.g. `gin` itself has
  `internal/` but no `cmd/`). The entry point is the exported identifiers
  of the root package — don't report "no entry point found," report the
  exported API.
- `internal/` holds code that cannot be imported by other modules — a real
  compiler-enforced boundary, not just convention, so it's the one place
  you can state a boundary as fact rather than inference.
- `pkg/` (if present) signals an intended external-facing API surface.

## Node / JavaScript library
- Entry point resolution order in `package.json`: `exports` (modern, can
  map several entry points and is authoritative when present) → `main`
  (legacy) → implicit `index.js` if neither is set. Express, for instance,
  declares **neither** `main` nor `exports` and relies on the implicit
  `index.js`, so "no `main` field" is not the same as "no entry point."
- `files` lists what actually ships to consumers — a useful second signal
  for the real public surface when `exports` is absent.
- `type: "module"` vs. CommonJS changes how imports resolve; note it, since
  it affects how consumers use the package.

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
