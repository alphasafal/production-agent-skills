# Migrations, rollout and rollback

## The invariant

During a rolling deploy, the old and new versions of the app run at the
same time against one database. After a rollback, the old version runs
against whatever schema the migration left. So every schema state must be
compatible with **both** the version being replaced and the version being
deployed. A migration review is checking that invariant, not SQL syntax.

## Classify each migration

| Change | Class | Safe to run before new code? | Safe in same release as code change? |
|---|---|---|---|
| Add nullable column / new table / new index (concurrently) | Expand | Yes | Yes |
| Add NOT NULL column with default | Expand (check lock behavior on large tables) | Yes | Yes |
| Backfill data | Expand | Yes, batched | Yes |
| Drop column / table | Contract | **No** | **No** — later release |
| Rename column / table | Contract (old name disappears) | No | No — use add + dual-write + drop |
| Change type / tighten constraint | Contract | No | Usually no |
| Drop an index the old code relies on | Contract | No | No |

## Expand / contract sequence

For "rename `legacy_email` to `email`" or "stop using column X":

1. **Expand** (release N): add the new column; code writes both, reads old
   (or new with fallback). Backfill.
2. **Migrate reads** (release N+1): code reads only the new column, still
   tolerates the old column existing. No schema change.
3. **Contract** (release N+2, after N+1 is fully rolled out and N is no
   longer a rollback target): drop the old column.

The finding to write when a drop ships with the code that stops reading
the column: the previous version still reads it while the rollout is in
progress, and rolling back after the migration breaks the old version.
Fix is to split the drop into a later release.

## Ordering in the pipeline

- **Expand migrations run before the new code is deployed**, in a separate
  job the deploy `needs:`. If the migration fails, nothing new is live.
- **Contract migrations run in a later release, after** the code that
  stopped using the object is fully live.
- Migration after deploy is wrong for both: new code serves against a
  missing schema (expand), or old tasks still serving lose their column
  (contract).
- Long-running migrations (big backfills, index builds) should not be in
  the deploy critical path; use online/concurrent index builds and batched
  backfills.
- Take a snapshot or confirm point-in-time recovery before any destructive
  step. Destructive migrations have no rollback; "down" migrations cannot
  restore dropped data.
- Serialize migrations with the deploy concurrency group so two runs do not
  migrate concurrently.

## Health gates and rollout

Deploy is not done when the API accepts the request. Look for:

- **Wait for stable**: `aws ecs wait services-stable`, `kubectl rollout
  status --timeout`, `helm upgrade --wait --atomic`, Argo Rollouts analysis.
- **Health/readiness**: Kubernetes `readinessProbe` (gates traffic) and
  `livenessProbe` (restarts); load balancer health checks; a post-deploy
  smoke test hitting a real endpoint, failing the job on non-2xx.
- **Progressive rollout**: rolling update with `maxUnavailable: 0`; canary
  (Argo Rollouts, Flagger, CodeDeploy, ECS blue/green) with automatic
  abort on error rate or latency; feature flags for risky behavior.
- **Circuit breaker**: ECS `deploymentCircuitBreaker: {enable: true,
  rollback: true}`; Helm `--atomic`.

## Rollback

A review should be able to answer: how do we get back to the previous
version in under 10 minutes, and does that work after this release's
migration?

- **Automated**: circuit breaker / `--atomic` / canary abort.
- **Documented**: exact command (`aws ecs update-service --task-definition
  <previous-revision>`, `helm rollback <release> <rev>`, `kubectl rollout
  undo`), who can run it, and where the previous artifact lives.
- Rollback is only real if the previous version is still compatible with
  the current schema — tie this back to the expand/contract check.
- Deploy scripts need `set -euo pipefail`; otherwise a failed command
  mid-script is followed by "Deploy complete" and exit 0.

## Fix snippet: migrate-then-deploy jobs

```yaml
  migrate:
    needs: test
    environment: production
    concurrency: { group: deploy-production, cancel-in-progress: false }
    steps:
      - run: npx knex migrate:latest --env production   # expand-only migrations
  deploy:
    needs: migrate
    environment: production
    concurrency: { group: deploy-production, cancel-in-progress: false }
    steps:
      - run: ./scripts/deploy.sh "$GITHUB_SHA"
      - run: aws ecs wait services-stable --cluster prod --services api
      - run: curl -fsS --retry 5 https://api.example.com/healthz
```
