# API Contracts & Backward Compatibility Checklist

## Public API / wire format changes
- [ ] A field removed or renamed in a response breaks existing consumers —
      confirm whether this API has external/unversioned consumers before
      treating a rename as safe.
- [ ] A field made required that was previously optional breaks existing
      clients sending the old shape.
- [ ] Enum values added are handled gracefully by existing consumers
      (or documented as a breaking addition if consumers use exhaustive
      matching).
- [ ] Changed status codes / error shapes are compatible with how existing
      clients handle errors.

## Database schema changes
- [ ] A column drop/rename is preceded by a migration strategy that doesn't
      break code still running the old version during a rolling deploy
      (expand-contract pattern: add new, migrate reads/writes, then remove
      old in a later deploy).
- [ ] A new `NOT NULL` column either has a default or a backfill step —
      check it won't fail on existing rows.
- [ ] New indexes needed for a new query pattern are actually added (check
      for missing indexes on new WHERE/JOIN columns, not just presence of
      the query).

## Versioning
- [ ] If the project has an API versioning scheme, the change respects it
      (new version for a breaking change, not a silent change to an
      existing version).
- [ ] Deprecation of an old field/endpoint is signaled (docs, deprecation
      header, changelog) rather than silently removed.

## Internal contracts (function/module signatures)
- [ ] A changed function signature's callers are all updated in this diff —
      grep for other call sites, don't assume the diff is complete.
- [ ] A changed shared type/interface is checked against all implementers,
      not just the one this diff was written for.
