# Deployment Checklist Patterns

Tailor to the actual change — not every item applies to every feature.

## Database changes
- [ ] Migration is backward compatible with the currently-deployed code
      (expand-contract: add new schema first, deploy code that can handle
      both old and new, backfill, then remove old schema in a later deploy).
- [ ] Migration has been tested against a production-like data volume if
      the table is large (a migration that's instant on 100 rows can lock
      a table for minutes at 100M rows).
- [ ] Backfill jobs (if any) are idempotent and can be safely re-run.

## Feature flags
- [ ] New behavior is behind a flag if it needs gradual rollout or a fast
      kill switch, rather than being live for 100% of traffic on deploy.
- [ ] Flag defaults to the safe/old behavior if the flag system itself
      fails to load.

## Configuration
- [ ] New required config/env vars are documented and set in every
      environment before the deploy that needs them (a deploy that
      introduces a required config it needs but isn't yet set will crash
      on startup or fail at first use).

## Monitoring
- [ ] Know what to watch immediately after deploy: error rate, latency on
      the changed path, and any new metric specific to this feature.
- [ ] An alert or dashboard exists for the new failure modes this change
      could introduce, not just pre-existing ones.

## Rollout sequencing
- [ ] If multiple services need to deploy together, the order that keeps
      the system working at every intermediate step is identified (usually:
      deploy the consumer of a new contract before the producer starts
      using it, or vice versa depending on the direction of the change).
