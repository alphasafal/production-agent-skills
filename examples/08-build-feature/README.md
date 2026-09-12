# Example 8: Build a Feature End to End

**Skill**: [feature-to-production](../../skills/feature-to-production/)
(composes with [repo-architect](../../skills/repo-architect/),
[production-code-review](../../skills/production-code-review/), and
[debugging-investigator](../../skills/debugging-investigator/) — see
[`docs/composing-skills.md`](../../docs/composing-skills.md), Pipeline A)

## Try it

Ask an agent with `feature-to-production` installed:

> "Add rate limiting to our public API — 100 requests per minute per API key. Ship it."

## What a correct run produces

Tests written for the acceptance criteria (429 + `Retry-After` beyond the
limit), the implementation itself, a deployment checklist (this scenario's
correct answer recommends a feature-flagged rollout), and a rollback plan
specific to this change (a flag flip — there's no persisted state
migration to worry about here, and a correct run should recognize that
rather than over-engineering the rollback plan).

## Reference answer

[`skills/feature-to-production/examples/add-rate-limiting-walkthrough.md`](../../skills/feature-to-production/examples/add-rate-limiting-walkthrough.md) —
note step 8, where it hands off to `production-code-review` mid-workflow.

## Grading a real run

See [`evaluations/workflows/feature-to-production.json`](../../evaluations/workflows/feature-to-production.json).
