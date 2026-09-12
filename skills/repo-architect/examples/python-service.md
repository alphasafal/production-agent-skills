# Example: Python service (FastAPI)

**Prompt:** "Map out this repo before I add a new endpoint."

Abridged ARCHITECTURE.md output:

> **System**: FastAPI service, modular-monolith layout. Entry point
> `app/main.py` builds the app via `create_app()` and includes routers from
> `app/routers/*.py`.
>
> **Layering**: `routers/` (HTTP handlers, request/response models via
> Pydantic) → `services/` (business logic, framework-agnostic) →
> `repositories/` (SQLAlchemy queries) → Postgres. Handlers do not call
> SQLAlchemy directly anywhere checked — the layering is consistently
> followed.
>
> **Entry points beyond HTTP**: `app/worker.py` is a separate process
> consuming from a Redis-backed queue (`rq`) for async email sending —
> easy to miss if only `main.py` is read.
>
> **Persistence**: Postgres via SQLAlchemy, Alembic migrations in
> `alembic/versions/`. Redis used both as the queue backend and as a cache
> (`services/cache.py`) — two different responsibilities on one Redis
> instance, worth noting.
>
> **External integrations**: SendGrid (email, via the worker), Auth0 (JWT
> verification middleware in `app/middleware/auth.py`).

Abridged MODULE_MAP.md excerpt:

> - `app/routers/orders.py` — order CRUD + checkout initiation endpoints.
> - `app/services/pricing.py` — discount/tax calculation, pure functions,
>   well-covered by unit tests.
> - `app/repositories/orders.py` — all order-table SQL, no other file
>   queries this table directly.
