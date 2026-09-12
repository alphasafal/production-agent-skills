# Concurrency & Performance Review Checklist

## Concurrency / shared state
- [ ] Shared mutable state (cache, counter, connection pool) accessed from
      multiple threads/async tasks is properly synchronized.
- [ ] No check-then-act race on a value another request/thread could change
      between the check and the act (see debugging-investigator's
      concurrency-debugging reference for the general mechanism).
- [ ] Async code awaits what it needs to before proceeding — no fire-and-
      forget on something whose result/completion matters.
- [ ] New locks are acquired in a consistent order relative to existing
      locks (deadlock risk otherwise).

## Idempotency
- [ ] Operations that can be retried (by a client, a queue, a load balancer)
      are idempotent, or protected by an idempotency key / unique constraint.

## Performance
- [ ] No new N+1 query/request pattern introduced (a loop issuing one
      DB/API call per item instead of a batched call).
- [ ] No accidentally quadratic or worse algorithm on a path that scales
      with user data (nested loops over the same growing collection).
- [ ] New hot-path code doesn't add unbounded allocation, unnecessary
      copying, or synchronous I/O on a path previously async/non-blocking.
- [ ] Pagination/limits exist on any new endpoint returning a collection
      that can grow unboundedly.

## Resource usage
- [ ] New connections (DB, HTTP client, file handles) are properly closed/
      released, including on the error path.
- [ ] Timeouts are set on new outbound calls — an unbounded wait on a
      dependency becomes an unbounded wait on this service too.
