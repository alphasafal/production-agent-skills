# Concurrency Debugging (races, deadlocks, intermittent failures)

A bug that only sometimes reproduces is still evidence-driven debugging — the
evidence is "fails N% of the time under condition X," not a shrug.

Evidence sources:

1. **A reproduction rate under a controlled trigger** — e.g. "fails ~1 in 20
   runs when two requests hit the same resource within 5ms." A bare "it's
   flaky" is not yet a minimized reproduction.
2. **Thread/goroutine/async-task dumps** at the moment of failure, if
   obtainable, showing what was actually running concurrently.
3. **Ordering of the actual interleaving that caused the failure** — inferred
   from logs with high-resolution timestamps and request/thread IDs, not
   assumed from reading the code sequentially.
4. **Lock/mutex/semaphore state** at failure time, for deadlocks.

## Common mechanisms worth checking as hypotheses

- **Check-then-act race**: code checks a condition then acts on it, with
  another thread/process able to invalidate the condition in between
  (classic TOCTOU — check the gap, not just the check and the act).
- **Missing or wrong-granularity locking**: a shared mutable structure
  (cache, counter, connection pool) is read/written without synchronization,
  or locked at a granularity that still allows the interleaving.
- **Non-atomic read-modify-write** on something assumed atomic (e.g.
  `counter += 1` across threads without a lock or atomic primitive).
- **Idempotency violated under concurrent duplicate requests** — see
  network-debugging.md; the concurrency angle is *two* near-simultaneous
  requests racing to both "win" a non-idempotent operation.
- **Deadlock from inconsistent lock ordering** across two code paths that
  both acquire the same two locks in different orders.

## Testing a concurrency hypothesis

Prefer a test that forces the interleaving deterministically (barriers,
explicit thread coordination, or a stress test with high iteration count)
over "run it a lot and see." A hypothesis is only confirmed once you can
reproduce the specific interleaving on demand, or strongly correlate its
absence with the fix.

## Evidence checklist

- [ ] A quantified reproduction rate and the triggering condition
- [ ] Timestamps/IDs establishing the actual interleaving, not an assumed one
- [ ] Confirmation the fix changes the reproduction rate to ~0, not just "seems better"
