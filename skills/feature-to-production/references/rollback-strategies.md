# Rollback Strategy Patterns

## Simple code-only change, no persisted state implications

A plain revert of the commit/deploy is a sufficient rollback plan — say so
explicitly rather than over-engineering a plan for a change that doesn't
need one.

## Change behind a feature flag

Rollback = flip the flag off. This is usually the fastest, lowest-risk
rollback available — prefer it for anything with meaningful user-facing
risk when the team has flag infrastructure.

## Change involving a database migration

- **Additive migration** (new column/table, nothing removed): rolling back
  the code is safe; the schema addition can stay (or be cleaned up later)
  without breaking the old code.
- **Destructive migration** (column/table removed or renamed): rolling back
  the code after a destructive migration has already run will break,
  because the old code expects schema that no longer exists. This is why
  destructive migrations should be a separate, later deploy after the
  expand-contract pattern's "contract" phase — confirm the actual migration
  approach follows this before calling a plain revert sufficient.

## Change with external side effects (emails sent, webhooks fired, charges made)

A code rollback doesn't undo side effects that already happened. State
explicitly whether any already-triggered side effects need separate
remediation (e.g. a batch of incorrectly-sent notifications) — this is not
covered by "revert the deploy."

## What every rollback plan should state explicitly

1. The specific mechanism (flag flip / code revert / migration-aware revert).
2. Anything that does NOT get undone by that mechanism.
3. Who/what needs to be notified if a rollback happens (if relevant to the
   project's practices).
