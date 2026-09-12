# Example 3: Review Code

**Skill**: [production-code-review](../../skills/production-code-review/)

## Try it

Feed an agent with `production-code-review` installed the fixture diff at
[`evaluations/fixtures/payments_endpoint.diff`](../../evaluations/fixtures/payments_endpoint.diff)
(a new payment endpoint with a real concurrency bug and no tests) and ask:

> "Review this PR before I merge it."

## What a correct run produces

A findings list, most severe first, each with severity (P0-P3),
classification (FACT / LIKELY RISK / OPTIONAL IMPROVEMENT), file/location,
evidence, impact, and a recommended fix — ending in a merge recommendation
that matches the severities found.

## Reference answer

[`skills/production-code-review/examples/idempotency-key-review.md`](../../skills/production-code-review/examples/idempotency-key-review.md)
reviews this exact fixture end to end — compare your agent's output
against it.

## Grading a real run

See [`evaluations/workflows/production-code-review.json`](../../evaluations/workflows/production-code-review.json).
