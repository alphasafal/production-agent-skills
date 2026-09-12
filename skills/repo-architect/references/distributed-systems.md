# Distributed Systems Mapping

Applies when the repo (or the system it's part of) involves multiple
services communicating over the network — whether all services live in this
repo or this repo is one of several.

## What to look for

- **Communication style**: synchronous (REST/gRPC) vs. asynchronous
  (message queue, event stream). Check actual client/producer code, not
  just infrastructure config — a repo can have Kafka config present but
  unused.
- **Service contracts**: where are they defined? (OpenAPI/proto files,
  shared type packages, or just implicit agreement — the latter is itself
  a risk worth flagging).
- **Service discovery / addressing**: hard-coded URLs, env-var-based
  config, or a service mesh/registry. Determines how deploy-order
  dependencies work.
- **Data ownership**: which service owns which data, and how do others get
  it (direct DB access — a red flag for tight coupling — vs. API calls vs.
  event-driven replication).
- **Failure handling at the boundary**: timeouts, retries, circuit breakers,
  fallback behavior when a dependency is unavailable — note if absent.

## Mapping approach

1. List the services this repo talks to (outbound) and what talks to it
   (inbound), from actual client code/route definitions — not architecture
   diagrams that may be stale.
2. For each boundary, note: protocol, contract source of truth, and
   failure-handling behavior.
3. Flag any place where a "distributed" call is actually synchronous and
   blocking in a way that couples availability across services.

## Risks specific to distributed systems worth registering

- No idempotency key on operations that can be retried across a network
  boundary (see the debugging-investigator skill's network/concurrency
  references for the failure modes this produces).
- Implicit contracts (no schema, no versioning strategy) between services
  owned by different teams.
- Cross-service transactions without a saga/compensation pattern — partial
  failure leaves data inconsistent.
