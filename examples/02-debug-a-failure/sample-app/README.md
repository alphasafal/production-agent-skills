# Sample App: Order Payment Service (buggy, on purpose)

A tiny in-memory order/payment service, pure Python standard library, no
network, no external dependencies, no credentials needed. This exists to
demonstrate [`skills/debugging-investigator/`](../../../skills/debugging-investigator/)
against a real, reproducible bug.

## Running it

```bash
cd examples/02-debug-a-failure/sample-app
python3 reproduce_bug.py
```

You should see:

```
Worker results: ['charged', 'charged']
Payments recorded for order-1: 2
BUG REPRODUCED: order-1 was charged more than once.
```

## The task

> "This service occasionally charges an order twice. Investigate and fix it."

Try it yourself first — ideally with an agent using the
`debugging-investigator` skill — before opening `BUG_SPOILER.md`. The point
of this example is to see whether the investigation actually reproduces
the bug, gathers evidence, and confirms a specific mechanism before
touching any code, per that skill's workflow.

## Files

- `app.py` — the service (`OrderStore`, `process_payment`). This is what
  has the bug.
- `reproduce_bug.py` — fires two concurrent payment requests for the same
  order and reports whether it duplicated.
- `BUG_SPOILER.md` — the known root cause and fix. Only for checking your
  work (or an agent's) afterward, not for reading first.

## Why this bug specifically

It's the same failure mode described in
`skills/debugging-investigator/examples/duplicate-payment-investigation.md`
and used in `skills/production-code-review/examples/idempotency-key-review.md`
— chosen deliberately so all three (the skill's own worked example, a code
review of the same pattern, and this runnable app) reinforce each other.
