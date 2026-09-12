# Worked example: reviewing a new payment endpoint

**Prompt:** "Review this PR before I merge it" (diff adds `POST /payments`
that charges a card and inserts an `orders` row, no idempotency handling,
no test for concurrent requests).

Abridged review output:

---

### P0 — FACT — `api/payments.py:42`
**Evidence**: handler reads `order.status`, then calls
`stripe.charges.create(...)`, then writes `order.status = 'paid'` as three
separate, unsynchronized statements with no unique constraint on
`payments.order_id`.
**Impact**: a client retry (or a double-click, or a network-level duplicate
request) can charge the customer twice for the same order.
**Recommended fix**: wrap the read-check-charge-write in a transaction using
`SELECT ... FOR UPDATE` on the order row, and add a unique constraint on
`payments.order_id` as a hard backstop.

### P1 — FACT — `api/payments.py:38`
**Evidence**: no `try`/`except` around `stripe.charges.create(...)`; a
Stripe API error propagates as an unhandled 500 with a raw stack trace in
the response body (confirmed by reading the global error handler, which has
no special case here).
**Impact**: card-decline and other expected Stripe errors surface as opaque
server errors instead of actionable client-facing messages, and may leak
internal details in the response.
**Recommended fix**: catch `stripe.error.CardError` and related exceptions
explicitly, return a structured 4xx with a client-safe message.

### P2 — LIKELY RISK — `api/payments.py` (whole file)
**Evidence**: no test file found under `tests/api/test_payments.py` or
equivalent for this new endpoint.
**Impact**: the P0 race condition above would have been much easier to
catch with a concurrent-request test; its absence is itself a gap on the
highest-risk endpoint in this diff.
**Recommended fix**: add a test asserting exactly one payment row after two
concurrent requests for the same order (this becomes the regression test
once the P0 fix lands).

### P3 — OPTIONAL IMPROVEMENT — `api/payments.py:15`
**Evidence**: `amount` is passed as a raw float to Stripe.
**Impact**: floating-point cents can round incorrectly at the margins;
Stripe expects integer minor units.
**Recommended fix**: convert to integer cents explicitly before the API call.

**Merge recommendation**: Not safe to merge as-is — the P0 double-charge
risk must be fixed first. P1 should also be addressed before shipping to
production; P2/P3 can follow in fast-follow PRs if time-boxed.
