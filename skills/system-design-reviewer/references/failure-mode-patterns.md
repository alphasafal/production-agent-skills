# Failure Mode Patterns

Use these to generate concrete failure scenarios (step 12) instead of a
generic "handle failures gracefully" recommendation.

## Dependency failure
- **Downstream is down**: does the caller time out and degrade, or hang
  indefinitely? Is there a fallback (cached value, default response) or
  does the failure propagate?
- **Downstream is slow, not down**: a slow dependency without a timeout
  budget can exhaust the caller's own thread/connection pool, turning one
  slow dependency into a full outage of the caller (thread-pool starvation).
- **Downstream returns partial/malformed data**: does the caller validate
  the response shape, or trust it and propagate corruption downstream?

## Retry behavior
- **Retry without backoff** on a struggling dependency amplifies load
  exactly when it's least able to handle it (retry storm).
- **Retry of a non-idempotent operation** produces duplicates — check every
  retried operation for an idempotency mechanism.
- **No retry at all** on a transient failure (e.g. a single dropped
  connection) pushes unnecessary failures up to the end user.

## Partial failure across multiple writes
- A single logical operation that writes to two systems (e.g. DB + queue,
  or two services) without a transaction or saga can leave them
  inconsistent if the second write fails. Name the specific inconsistency
  that results, not just "consistency could be an issue."

## Cascading failure
- One overloaded/slow component causes callers to queue up requests,
  which then overload *their* callers — trace this chain explicitly for
  any synchronous call graph with no circuit breaker or bulkhead.

## Degraded-mode behavior
- When a non-critical dependency (e.g. a recommendation service) is down,
  does the system degrade gracefully (skip the feature) or fail the whole
  request? This is often the highest-leverage resilience question to ask.
