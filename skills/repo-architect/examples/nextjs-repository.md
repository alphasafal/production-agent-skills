# Example: Next.js repository

**Prompt:** "I just cloned this Next.js app, help me understand it before I
touch the checkout flow."

Abridged ARCHITECTURE.md output:

> **System**: Next.js 14 App Router app, hybrid rendering (server components
> by default, client components opted in via `"use client"`). Deployed as a
> single Vercel-style Node server (`next start` in the Dockerfile).
>
> **Entry points**: `app/**/page.tsx` (pages), `app/api/**/route.ts`
> (backend endpoints — `app/api/checkout/route.ts` handles payment intent
> creation), `middleware.ts` (auth redirect for `/account/*`).
>
> **Data flow (checkout)**: `app/checkout/page.tsx` (server component) →
> fetches cart via `lib/cart.ts` → renders `CheckoutForm` (client component)
> → on submit, POSTs to `app/api/checkout/route.ts` → calls Stripe SDK →
> writes `orders` row via `lib/db.ts` (Prisma) → redirects to `/orders/[id]`.
>
> **Persistence**: Postgres via Prisma (`prisma/schema.prisma`), migrations
> in `prisma/migrations/`.
>
> **External integrations**: Stripe (payments), Resend (transactional email
> on order confirmation, triggered from the same API route).

Abridged RISK_REGISTER.md excerpt:

> - `app/api/checkout/route.ts` writes the order row and calls Stripe in
>   sequence with no visible idempotency key — a client retry on timeout
>   could plausibly double-charge. Worth a targeted look with
>   `debugging-investigator` if duplicate orders are ever reported.
> - No tests found under `app/api/checkout/` — the highest-risk endpoint in
>   the app currently has no automated coverage.
