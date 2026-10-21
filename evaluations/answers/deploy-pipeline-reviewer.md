# Answer key: deploy-pipeline-reviewer workflow-01

Grader-only. Fixture: `evaluations/fixtures/deploy-pipeline-reviewer/`.
Scenario: "We're about to turn on this new deploy pipeline for production. Review it first."

Correct conclusion: **NO-GO.** The pipeline must not be enabled as-is. At least
three independent P0s (untrusted PR code running with prod secrets and a
write-all token, secrets written to a downloadable artifact, and a
destructive migration that breaks rollback and in-flight old tasks), plus
ungated prod deploys from any branch.

## Planted issues

Line numbers refer to the fixture files as committed.

| # | Sev | File:line | Issue | Why it matters | Expected fix |
|---|---|---|---|---|---|
| 1 | P0 | `.github/workflows/deploy.yml:7-8`, `:23`, `:40` | `pull_request_target` trigger + `actions/checkout` of `github.event.pull_request.head.sha` in both jobs | `pull_request_target` runs in the base repo context with secrets and a write token. Checking out the PR head runs attacker-controlled code (`npm ci` lifecycle scripts, `npm test`, `./scripts/deploy.sh`, the Dockerfile) with `AWS_*`, `PROD_DATABASE_URL`, `SLACK_WEBHOOK`. Any fork PR can exfiltrate prod credentials or deploy itself to prod. | Remove `pull_request_target`; run tests on `pull_request` (no secrets). Deploy only on `push` to `main` checking out `github.sha` (default). If a privileged PR workflow is ever needed, never check out head code in it. |
| 2 | P0 | `.github/workflows/deploy.yml:10` | `permissions: write-all` at workflow level | Every job gets a token that can push code, edit releases, approve/merge PRs. Combined with #1, a fork PR can push to `main`. | `permissions: contents: read` at top; grant `id-token: write` only on the deploy job (for OIDC). |
| 3 | P0 | `.github/workflows/deploy.yml:45-46`, `:76-81` | Secret debug logging: `echo ... $AWS_SECRET_ACCESS_KEY`; `env \| sort > deploy-env.txt` uploaded as artifact with `if: always()` | Log masking hides the echoed value in the step log (still a red flag: any transform such as base64 or substring bypasses masking), but the artifact file is **not masked** — it contains AWS keys and the prod DB URL, downloadable by anyone with read access to Actions, retained for 90 days. | Delete the debug step and the artifact upload. Rotate the AWS keys, DB password and Slack webhook if this ever ran. |
| 4 | P1 | `.github/workflows/deploy.yml:4-6`, `:31` | Deploy runs on `push` to any branch (`"**"`) and on every PR; deploy job has no `if:` guard | Any pushed branch, or any PR, deploys to production. | `on: push: branches: [main]`; `if: github.ref == 'refs/heads/main'` on deploy job. |
| 5 | P1 | `.github/workflows/deploy.yml:31` | Deploy job has no `needs: test` | Jobs run in parallel; deploy proceeds even when tests fail. | `needs: test`. |
| 6 | P1 | `.github/workflows/deploy.yml:31` | No `environment:` on deploy job | No required reviewers, no branch restriction, no environment-scoped secrets; repo-level secrets available to every job and branch. | `environment: production` with required reviewers + "selected branches: main"; move prod secrets to the environment. |
| 7 | P0 | `migrations/0042_drop_legacy_email_column.sql:5`, `CHANGELOG.md` 2.8.0, `deploy.yml:64-68` | Destructive `DROP COLUMN` shipped in the same release that stops reading it; runs right after a deploy that only "submits" | `deploy.sh` returns as soon as ECS accepts the update, so 2.7.x tasks (which still read the `legacy_email` fallback) are still serving when the column is dropped: errors during rollout. Rolling back to 2.7.x after the migration is impossible without restoring data. Not reversible. | Expand/contract: ship 2.8.0 code-only; wait until no running or rollback-target version reads the column; drop it in a later release. Pipeline: run additive (expand) migrations **before** deploy, gated; contract migrations in a separate later release. Take a backup / snapshot before any destructive step. |
| 8 | P1 | `.github/workflows/deploy.yml:64-68` | Migration step ordered after deploy (general ordering) | For any additive migration, new code is live before its schema exists; if the migration fails, new code is already serving against the wrong schema with no rollback. | Migrate (expand) before deploy, in its own job that the deploy `needs:`. |
| 9 | P1 | `scripts/deploy.sh` (whole file; lines 1-15) | No `set -euo pipefail`; no wait for stability; no health check; no rollback | If `shipctl render-task` fails, `aws ecs update-service` runs with an empty `--task-definition` and the script still prints "Deploy submitted" and exits 0 from the last `echo`. Pipeline reports success without verifying the service is healthy. No documented or automated rollback path. | `set -euo pipefail`; `aws ecs wait services-stable`; smoke-test a health endpoint; enable ECS deployment circuit breaker with rollback; document rollback (previous task definition revision). |
| 10 | P2 | `scripts/deploy.sh:5` + `deploy.yml:33-36` | `ECR_REGISTRY` is only interpolated as `${{ secrets.ECR_REGISTRY }}` in workflow steps, never exported to the step env, so in `deploy.sh` it is empty and `IMAGE` becomes `/orders-api:<sha>` | Deploy references a non-existent image; without `set -u` this is silent. (Bonus finding — credit if found.) | Export `ECR_REGISTRY` in env; `set -u`. |
| 11 | P1 | `.github/workflows/deploy.yml:49` | `curl -fsSL https://get.shipctl.dev/install.sh \| bash` in a job holding prod secrets | Unverified remote script executes with AWS keys and DB URL in env; a compromised host or DNS = prod compromise. Unpinned version. | Download a pinned release, verify checksum/signature, or use a pinned action/container. |
| 12 | P1 | `.github/workflows/deploy.yml:71` | Third-party action pinned to `@main` with `SLACK_WEBHOOK` secret and job-wide AWS/DB env | Mutable ref: whatever is on that branch at run time executes in the deploy job and can read the job env. | Pin to a full commit SHA (with version comment); scope the step env narrowly. |
| 13 | P2 | `.github/workflows/deploy.yml:21`, `:24`, `:38`, `:52`, `:78` | First-party / vendor actions pinned by tag (`@v4`) | Tags are mutable; lower risk for `actions/*` and `aws-actions/*` than #12, but the repo's own lint workflow already shows SHA pinning. | Pin to SHAs; Dependabot for updates. |
| 14 | P1 | `.github/workflows/deploy.yml:34-35`, `:51-56` | Long-lived AWS access keys instead of OIDC | Static keys leak (see #3) and don't expire. | `aws-actions/configure-aws-credentials` with `role-to-assume` + `id-token: write`; trust policy limited to `repo:<org>/<repo>:environment:production`. |
| 15 | P2 | `.github/workflows/deploy.yml` (no `concurrency:` anywhere) | Overlapping deploys race | Two pushes deploy and migrate concurrently; older SHA can finish last. | `concurrency: { group: deploy-production, cancel-in-progress: false }` on the deploy job. |
| 16 | P2 | `.github/workflows/deploy.yml:27` with `:7` | `cache: npm` populated from PR-head code under `pull_request_target` | Cache poisoning: a fork PR can write a poisoned cache entry later restored by trusted runs. | Fixed by #1; do not use caches in privileged workflows that run untrusted code. |
| 17 | P1 | `Dockerfile:9` (also `:8`) | `.env` copied into the image | Secrets baked into image layers in ECR; anyone who can pull the image has them; persists in layer history. `COPY . .` also copies it without a `.dockerignore`. | Remove the COPY; add `.dockerignore` with `.env`; inject config at runtime (ECS secrets / SSM). |
| 18 | P2 | `Dockerfile:1` | `FROM node:latest` | Non-reproducible; major Node version can change under you. | `FROM node:20.x-slim@sha256:<digest>`. |
| 19 | P2 | `Dockerfile` (no `USER`) | Runs as root | Container escape / write blast radius. | `USER node`. |
| 20 | P3 | `Dockerfile:6` | `npm install` instead of `npm ci`, dev deps included | Non-reproducible, larger image. | `npm ci --omit=dev`. |
| 21 | P2 | `deploy.yml` (no step after deploy) | No health check / readiness gate after deploy; no progressive rollout | Broken releases go to 100% of traffic and the pipeline reports green. | Wait for stability + smoke test; ECS circuit breaker or canary. (Overlaps #9; credit either.) |

Severity ±1 on P2/P3 items is acceptable. Items 1, 3 and 7 must be P0 (or
explicitly blocking); 4/5/6 must be at least P1 and blocking.

## Decoy (must NOT be flagged as a defect)

`.github/workflows/lint.yml` — triggered on `pull_request` (not
`pull_request_target`), `permissions: contents: read`, no secrets, actions
pinned to full commit SHAs with version comments. This is the correct
pattern. A run that flags it as risky (e.g. "lint workflow runs untrusted PR
code", "permissions too broad", "unpinned") has produced a false positive.
Citing it as the model the deploy workflow should follow is good.

Also acceptable, not a defect: `src/db/customers.js` no longer reads
`legacy_email` — that is the intended app change; the problem is the
same-release drop, not the code.

## What a passing run looks like

- `PIPELINE_REVIEW.md` with an inventory of the files reviewed and a
  job-by-job trace of `deploy.yml` (trigger -> job -> step -> what secrets
  and token scope are live at that step).
- Findings ranked P0 first, each with file:line, evidence, impact, and a
  fix snippet (YAML/SQL/shell).
- Items 1, 3, 4/5/6 (together or separately) and 7 present; item 7 explains
  expand/contract and the old-tasks-still-running / rollback problem, not
  just "dropping columns is risky".
- Explicit NO-GO verdict with an ordered list of what must change before
  enabling, and secret rotation called out if the workflow has already run.
