# Backend Architecture Patterns

## What to look for

- **Application shape**: monolith, modular monolith (internal boundaries but
  one deployable), or a single microservice that's part of a larger system
  (check for service-discovery/mesh config indicating siblings exist
  elsewhere).
- **Entry points**: HTTP route registration (framework-specific — Express
  `app.use`/`router`, Django `urls.py`, Rails `routes.rb`, Go `net/http`
  or a router library), plus non-HTTP entry points: CLI commands, queue
  consumers/workers, scheduled jobs (cron config, `celery beat`, k8s
  CronJobs).
- **Layering**: is there a clear separation between transport (controllers/
  handlers), domain/business logic, and persistence? Or is DB access called
  directly from handlers? This materially affects how safely a change can
  be made — no separation means changes ripple further.
- **Configuration and secrets**: how environment-specific config is loaded
  (env vars, config files, a secrets manager) — relevant for the risk
  register if secrets appear to be handled unsafely.
- **Background/async work**: job queues, event consumers, outbox patterns —
  these are entry points too, often overlooked when mapping only HTTP routes.

## Common module organization patterns

- **By layer** (`controllers/`, `services/`, `repositories/` or `models/`) —
  trace one request through all three to understand the real data flow.
- **By domain/feature** (`orders/`, `users/`, `billing/`) each with its own
  internal layers — check whether domains call each other directly (tight
  coupling) or through defined interfaces/events (looser coupling).
- **Hexagonal/ports-and-adapters**: explicit `domain/`, `ports/` or
  `interfaces/`, and `adapters/` or `infrastructure/` directories — the
  domain layer should have no framework/DB imports; note any place that
  violates this as a risk.

## Data flow to trace

Entry point (route/consumer/cron) → validation → domain/business logic →
persistence read/write → external calls (if any) → response/side effect.

## Persistence details worth confirming, not assuming

- Which ORM/query builder is in use, and whether raw SQL is also used
  alongside it (common source of drift/inconsistency).
- Migration tool and whether migrations are applied automatically on deploy
  or manually — relevant to the risk register.
