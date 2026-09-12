# Network Debugging (timeouts, retries, cross-service calls)

Evidence sources:

1. **Actual request/response pairs with timestamps and headers** on both
   sides of the call, if accessible — client-observed latency and
   server-observed latency can disagree, and the gap is itself evidence.
2. **Timeout and retry configuration** — the literal values (connect timeout,
   read timeout, retry count, backoff), not what the code "should" be doing.
3. **Connection pool / keep-alive state** — exhausted pools produce symptoms
   that look like server-side slowness but aren't.
4. **DNS resolution and TLS handshake timing** if latency is inconsistent
   across hosts/regions.

## Common mechanisms worth checking as hypotheses

- **Retry storms**: a client retries on timeout without backoff, amplifying
  load on an already-slow dependency (look for correlated spikes).
- **Non-idempotent operation retried**: a POST retried after a timeout when
  the original request actually succeeded server-side — this produces
  duplicates, not just wasted work (see also database-debugging.md).
- **Timeout shorter than the operation's real P99**: the "failure" is
  actually a mismatched timeout budget, not a bug in the callee.
- **Partial response treated as success**: a truncated/chunked response
  wasn't fully read but the client proceeded as if it had the full payload.
- **Load balancer / proxy layer swallowing or rewriting headers** the
  application logic depends on (auth headers, correlation IDs).

## Evidence checklist

- [ ] Timeout/retry config values actually in effect (not just what's in a
      config file — confirm what was loaded at runtime)
- [ ] Timestamps from both sides of the call, if available
- [ ] Whether the "failed" request actually completed server-side
- [ ] Correlation/trace ID to follow the request across services
