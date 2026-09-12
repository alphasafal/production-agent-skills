# Worked example: Kafka vs. SQS for order events

**Prompt:** "We need to pick a message queue for order events between our
checkout service and fulfillment service. Kafka or SQS?"

Abridged output:

## RESEARCH.md (excerpt)
- SQS: fully managed, at-least-once delivery, no built-in replay beyond the
  retention window, per-message pricing. (Source: AWS SQS documentation.)
- Kafka: requires running/operating brokers (or a managed offering like
  MSK/Confluent Cloud), supports long retention and replay, higher
  operational complexity. (Source: Apache Kafka documentation.)
- Assumption (unverified): team has no prior Kafka operational experience —
  stated by the user, not independently verified.

## DECISION_MATRIX.md (excerpt)

| Criterion | SQS | Kafka |
|---|---|---|
| Operational complexity | Low (fully managed) | Higher (even managed offerings need topic/partition planning) |
| Team familiarity | Team has used SQS before | No prior experience (per user) |
| Replay/reprocessing need | Not a stated requirement | Would satisfy it, but not currently needed |
| Cost at current volume (~50k msgs/day) | Low, pay-per-message | Managed Kafka has a higher fixed floor cost at this volume |

## ADR.md (excerpt)

**Decision**: SQS.

**Consequences — given up**: replay/reprocessing capability Kafka would
provide, and Kafka's stronger fit if a second consumer service is added
later needing independent read position.

**Conditions that would change this decision**: if a second, independent
consumer of these events is added, or if event replay becomes a real
requirement, revisit — that's the scenario where Kafka's trade-offs would
start to pay off.
