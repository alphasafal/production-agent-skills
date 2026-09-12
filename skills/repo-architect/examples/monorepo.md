# Example: monorepo (Turborepo, JS/TS)

**Prompt:** "This is a Turborepo with a bunch of apps and packages, help me
find my way around before touching the `web` app's auth flow."

Abridged ARCHITECTURE.md output:

> **System**: Turborepo monorepo (`turbo.json`, `pnpm-workspace.yaml`).
> `apps/web` (Next.js customer app), `apps/admin` (Next.js internal admin
> app), `apps/api` (NestJS backend) are deployables; `packages/ui`,
> `packages/config`, `packages/auth-client` are shared libraries consumed
> by the apps.
>
> **Dependency graph** (from each app's `package.json` `dependencies` plus
> confirmed by actual imports): both `web` and `admin` depend on
> `packages/ui` and `packages/auth-client`; `api` does not depend on
> either (it's backend-only, has its own `packages/auth-server`).
>
> **Scoped investigation**: since the task is `web`'s auth flow, this
> mapping goes deep on `apps/web` and `packages/auth-client` only.
> `apps/admin` and `apps/api`'s internals were not fully mapped — noted
> as scoped out.
>
> **Auth flow in `web`**: `packages/auth-client` wraps a cookie-based
> session check and exposes a `useSession()` hook; `apps/web/middleware.ts`
> calls a server-side equivalent for route protection. Both must stay in
> sync if the session shape changes — flagged in the risk register since
> they're two independent implementations of the same check.

Abridged RISK_REGISTER.md excerpt:

> - `packages/auth-client`'s client-side session check and
>   `apps/web/middleware.ts`'s server-side check are separately implemented
>   rather than sharing one source of truth — a change to session shape
>   could silently desync them.
> - `turbo.json` pipeline doesn't declare `auth-client` as an input for
>   `web`'s build task cache key in the version checked — worth confirming
>   before relying on Turborepo's cache during this change.
