# Worked example: add rate limiting to the public API

**Prompt:** "Add rate limiting to our public API — 100 requests/minute per
API key."

Abridged walkthrough:

1. **Acceptance criteria**: requests beyond 100/min per key return 429 with
   a `Retry-After` header; requests under the limit are unaffected; limit
   resets on a rolling 1-minute window.
2. **Repository inspection** (`repo-architect`, brief since the API layer
   was already understood from earlier work): confirmed all public routes
   pass through one Express middleware chain — a single insertion point.
3. **Design**: smallest viable change is one new middleware using the
   existing Redis instance (already used for caching) for a sliding-window
   counter, inserted once in the shared middleware chain — not per-route.
4. **Affected interfaces**: grep confirmed only the shared middleware setup
   file registers route-level middleware; no route does its own separate
   registration that would bypass this.
5. **Tests**: added a test firing 101 requests with the same key within a
   window and asserting the 101st gets 429 with `Retry-After`; a second
   test confirms different keys have independent limits.
6. **Implementation**: the middleware, using `INCR` + `EXPIRE` on a
   per-key-per-window Redis key.
7. **Verification**: new tests pass; manually verified via the dev server
   that a burst of requests gets limited and the header is present.
8. **Code review** (`production-code-review`): flagged P2 — no metric
   emitted when a key gets rate-limited, recommended adding one for
   visibility into which keys are hitting limits. Fixed before merge.
9. **Deployment checklist**: no migration; requires Redis (already in use,
   no new infra); recommend deploying behind a flag defaulting to a high
   limit initially, then tightening to 100/min after confirming no
   legitimate traffic gets caught.
10. **Rollback**: flag flip to disable rate limiting entirely; no persisted
    state beyond transient Redis counters with short TTLs, so rollback has
    no lingering side effects.
