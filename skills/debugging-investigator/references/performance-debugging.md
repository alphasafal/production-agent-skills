# Performance Debugging (latency, throughput, resource usage)

The symptom here is a number, so the evidence must be numbers: profiles,
timing breakdowns, and resource graphs — not intuition about what "feels slow."

Evidence sources:

1. **A profile or timing breakdown of the slow path** (CPU profiler, flame
   graph, or manual timing instrumentation around suspected segments).
2. **Percentiles, not averages** — P50/P95/P99 tell very different stories
   than a mean; a regression that only shows in P99 usually points to a
   tail-latency mechanism (GC pause, lock contention, cold cache) rather
   than a uniformly slower code path.
3. **Resource graphs at the time of the regression** — CPU, memory, GC
   activity, connection pool saturation, disk I/O.
4. **A before/after comparison against a known-good baseline** (previous
   deploy, previous commit) run under comparable load.

## Common mechanisms worth checking as hypotheses

- **N+1 queries or requests**: a loop issuing one call per item instead of
  a batched call — check actual call counts, not just total time.
- **Unbounded or accidentally quadratic algorithm**: works fine at small
  scale, degrades sharply past some input size — check whether the
  regression correlates with a growing input rather than a code change.
- **GC pressure from excess allocation**: profile allocations, not just CPU
  time, if the language is garbage-collected and pauses appear in P99.
- **Lock contention**: multiple threads serializing on a shared resource
  that only shows up under concurrent load, not in a single-threaded repro.
- **Cold cache / cold start**: the "regression" is actually the first
  request after a deploy or scale-up event, not a steady-state problem.

## Evidence checklist

- [ ] A profile or timing breakdown, not a guess about which function is slow
- [ ] Percentile data, and which percentile actually regressed
- [ ] A load/traffic pattern comparison between the good and bad periods
- [ ] Confirmation the fix moves the actual percentile, not just a hunch
