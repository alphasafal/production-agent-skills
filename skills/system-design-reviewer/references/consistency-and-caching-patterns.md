# Consistency & Caching Patterns

Use these when reviewing steps 8-9 (consistency, caching).

## Consistency models to check the design actually delivers

- **Strong consistency**: every read sees the latest write. Usually means a
  single primary for the relevant data, or a consensus protocol
  (Raft/Paxos-backed store). If the design claims this over an async
  replica setup, that's a factual mismatch to flag, not a nitpick.
- **Read-your-writes**: a user sees their own write immediately, even if
  other users might not yet (often achieved by routing a user's reads to
  the primary or a replica known to have caught up).
- **Eventual consistency**: acceptable when the design and the product
  requirement agree on it — flag when the UI/UX implies immediacy the
  backend doesn't guarantee (e.g. "your comment was posted" while it's
  still propagating to the read replica the next request hits).

## Caching invalidation strategies (a cache without one of these is a bug)

- **TTL-based**: simple, but staleness window is real — check it's
  acceptable for the data (fine for a product catalog, not for an account
  balance).
- **Write-through**: cache updated synchronously with the write — adds
  latency to writes, keeps cache always fresh.
- **Cache invalidation on write**: explicit delete/update of the cache key
  when the underlying data changes — check every write path that should
  trigger it actually does (a common miss: a bulk-update/admin path that
  bypasses the normal write path and skips invalidation).
- **Event-driven invalidation**: a change event triggers invalidation
  asynchronously — introduces a window where the cache is stale; check if
  that window is acceptable.

## Cache-specific failure modes to check

- **Cache stampede**: many requests miss the cache simultaneously (e.g.
  right after a popular key expires) and all hit the origin at once —
  check for request coalescing or jittered TTLs.
- **Cached negative results**: caching "not found" without a shorter TTL
  or explicit invalidation can hide a resource that was created right
  after the miss was cached.
