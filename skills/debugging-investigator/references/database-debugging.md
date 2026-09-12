# Database Debugging

Evidence sources:

1. **The actual query and its `EXPLAIN`/`EXPLAIN ANALYZE` output** — not what
   the ORM is "supposed to" generate. Log or intercept the real SQL.
2. **Transaction isolation level and lock state** — for correctness bugs
   involving concurrent writers, check what isolation level is in effect and
   whether locks/deadlocks appear in the DB's own logs.
3. **Migration history** — `git log` on the migrations directory plus the
   DB's actual schema (`\d table` / `DESCRIBE table`) to catch drift between
   what the code assumes and what's actually deployed.
4. **Row-level data**, not just schema — a "duplicate key" bug is often a data
   problem (bad backfill, non-idempotent job) rather than a schema/logic bug.

## Common mechanisms worth checking as hypotheses

- **Lost update / write skew**: two transactions read-modify-write the same
  row without proper locking (`SELECT ... FOR UPDATE`) or optimistic
  concurrency (version column).
- **N+1 queries masquerading as a correctness bug**: a partial/incomplete
  result set because a batched load silently truncated.
- **Non-idempotent retry**: a request handler retried by a client or queue
  re-executes a non-idempotent insert, producing duplicates — check for a
  missing idempotency key or unique constraint.
- **Implicit type coercion in a WHERE clause** silently returning 0 or wrong
  rows (e.g. comparing a string column to an int parameter).
- **Migration applied out of order** across environments — verify the
  migration state table, don't assume the code and DB agree.

## Evidence checklist

- [ ] The exact SQL executed, with parameters
- [ ] `EXPLAIN ANALYZE` output if performance is in question
- [ ] Isolation level and any lock/deadlock log entries for concurrency bugs
- [ ] Actual row data for the affected keys, not a summary
