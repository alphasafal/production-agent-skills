# Example 6: Make a Technical Decision

**Skill**: [research-to-decision](../../skills/research-to-decision/)

## Try it

Ask an agent with `research-to-decision` installed:

> "We need to pick a message queue for order events between our checkout
> service and fulfillment service. Kafka or SQS? Research both and
> recommend one."

## What a correct run produces

`RESEARCH.md` (findings with sources, or explicit "assumption/unverified"
flags for anything that couldn't be checked), `DECISION_MATRIX.md`
(options scored against explicit, pre-stated criteria), and `ADR.md` (the
durable record, using
[`skills/research-to-decision/assets/adr-template.md`](../../skills/research-to-decision/assets/adr-template.md)) —
stating clearly what's given up, not just what's gained.

## Reference answer

[`skills/research-to-decision/examples/kafka-vs-sqs-decision.md`](../../skills/research-to-decision/examples/kafka-vs-sqs-decision.md).

## Grading a real run

See [`evaluations/workflows/research-to-decision.json`](../../evaluations/workflows/research-to-decision.json).
