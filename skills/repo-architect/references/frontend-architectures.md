# Frontend Architecture Patterns

## What to look for

- **Rendering model**: client-only SPA, server-rendered, or hybrid
  (Next.js/Nuxt/Remix-style). Check the framework config, not just presence
  of the framework as a dependency — an app can depend on Next.js and still
  be used purely as a client-side router.
- **State management**: local component state only, a global store (Redux,
  Zustand, Pinia), or server-state libraries (React Query, SWR, Apollo
  cache). This matters for data-flow mapping — server-state libraries make
  the "backend" boundary fuzzier because caching/refetch logic lives client-side.
- **Routing**: file-based (Next.js `app/`/`pages/`, Nuxt) vs. explicit route
  config (React Router). File-based routing means the entry-point map is
  largely the directory tree itself.
- **API boundary**: does the frontend call a separate backend, or does it
  have its own server functions/route handlers (Next.js API routes, Remix
  loaders/actions)? These count as backend entry points even in a
  "frontend" repo.
- **Build/bundling config**: `vite.config`, `next.config`, `webpack.config` —
  often encodes environment-specific behavior (proxying, env var injection)
  that affects data flow.

## Common module organization patterns

- **By feature** (`features/checkout/`, `features/auth/`) — modules are
  usually more self-contained; check for a shared/common directory that
  cuts across features.
- **By layer** (`components/`, `hooks/`, `services/`, `store/`) — trace a
  single feature across layers to understand data flow, since no single
  directory tells the whole story.
- **Design-system-first** (`ui/` or a separate package) — treat this as a
  dependency, not application logic, when mapping.

## Data flow to trace

Entry point (route) → data fetch (loader, hook, or effect) → state
(component/global) → render → user action → mutation/side effect → refetch
or optimistic update.
