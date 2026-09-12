# Worked example: intermittent duplicate payments

**User prompt:** "My API is occasionally returning duplicate payments — same
order gets charged twice. Find the root cause and fix it."

This shows the shape of a completed investigation using this skill's
workflow and output contract. Abridged for length.

---

## DEBUG_REPORT.md

### Symptoms
`POST /orders/:id/pay` occasionally results in two `payment.succeeded` rows
for the same order. Reported ~3 times in the last week, no clear trigger from
the user's description alone.

### Reproduction
Reproduced locally by firing two concurrent `POST /orders/:id/pay` requests
for the same order ID with a 5ms gap, using a script that races two requests.
Reproduces in roughly 1 in 8 attempts.

### Evidence
- Payment handler reads `order.status`, checks it's `pending`, then charges
  the card and writes `order.status = 'paid'` — as three separate statements,
  not one atomic operation.
- No unique constraint on `(order_id)` in the `payments` table.
- Access logs show both concurrent requests reading `status = 'pending'`
  before either write lands (~4ms apart).

### Rejected hypotheses
- **"Client retries on timeout"** — rejected: access logs show both requests
  originated from different client IPs at nearly the same timestamp, not a
  single client's retry pair.
- **"Payment gateway double-fires webhook"** — rejected: gateway dashboard
  shows exactly one charge event per request; the duplication is in our own
  order-status logic, not the gateway.

### Confirmed root cause
Check-then-act race in the payment handler: two concurrent requests for the
same order both read `status = 'pending'` before either request's write
completes, so both proceed to charge and both write a payment row. Confirmed
by reproducing the exact interleaving with a coordinated two-request test and
observing two payment rows.

### Minimal fix
Added a unique constraint on `payments.order_id` and wrapped the
read-check-charge-write sequence in a single transaction using
`SELECT ... FOR UPDATE` on the order row, so the second concurrent request
blocks until the first commits and then sees `status = 'paid'`.

### Regression protection
Added a test that fires two concurrent payment requests for the same order
and asserts exactly one `payments` row exists afterward. Fails against the
pre-fix handler, passes after.
