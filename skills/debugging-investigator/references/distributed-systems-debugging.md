# Distributed Systems Debugging

When a failure spans multiple services, the investigation is a search for
where the request/data diverged from expectation across a boundary.

Evidence sources:

1. **Distributed traces** (if instrumented) — follow one specific failing
   request/trace ID end to end rather than reasoning about the system in
   the abstract. If a tracing tool is connected (e.g. via MCP), query it
   for the actual failing trace before forming hypotheses.
2. **Per-service logs correlated by request/trace ID**, ordered by timestamp
   across services (careful: clocks can skew — treat causal order from
   trace spans as more reliable than wall-clock log timestamps alone).
3. **Service topology and the specific call path involved** — which services
   were actually in the path for this request, not the full architecture
   diagram.
4. **Deployment/version skew** — which version of each service was running
   at the time of the failure; a partial rollout is a common root cause.

## Common mechanisms worth checking as hypotheses

- **Partial rollout inconsistency**: some instances run the new version,
  some the old, and a request bounces between them assuming a shared
  contract that changed.
- **Cascading timeout**: an inner service's timeout exceeds an outer
  service's budget, so the outer service gives up and retries while the
  inner call is still in flight (compounds into a retry storm).
- **Eventual-consistency window read**: a read hits a replica or cache that
  hasn't yet observed a very recent write from another service.
- **Silent contract drift**: a schema/field change in one service is
  tolerated by lenient deserialization in another, producing wrong values
  instead of an error.
- **Message queue redelivery**: at-least-once delivery redelivers a message
  after a slow-but-successful handler, and the handler isn't idempotent.

## Evidence checklist

- [ ] One concrete failing trace/request ID followed end to end
- [ ] Version/deployment state of each service in the path at failure time
- [ ] Whether the same request path succeeds against a known-good version
