# Worked example: GitLab CI + Helm deploy for `billing-worker`

Request: "We're switching billing-worker from manual `helm upgrade` to a
GitLab pipeline. Can you review `.gitlab-ci.yml` and the chart before we
merge it?"

Files provided: `.gitlab-ci.yml`, `Dockerfile`, `chart/values.yaml`,
`chart/templates/deployment.yaml`, `chart/templates/migrate-job.yaml`,
`db/migrations/20260914_add_invoice_currency.sql`, `scripts/smoke.sh`.

Below is the `PIPELINE_REVIEW.md` a correct run produces.

---

# PIPELINE_REVIEW.md — billing-worker

## Verdict

**GO WITH CONDITIONS.** Fix the two P1s (tests can fail and still deploy;
non-atomic Helm upgrade with migration in the post-upgrade position) before
the first production run. No secret exposure found.

## Scope

Reviewed: all seven files above. Referenced but not reviewed:
`registry.example.com/platform/helm-kubectl:3.15` (internal image, pinned
by digest; contents not inspected).

Assumptions (not visible in the repo):
- `main` is a protected branch and `KUBE_CONFIG_PROD` is a protected,
  masked variable. If it is not protected, any branch pipeline can read it
  and finding 3 becomes P0.
- The `production` environment has "Allowed to deploy: Maintainers".

## Pipeline trace

Triggers: `workflow: rules` — merge request pipelines and pushes to `main`.

| Job | Stage | Runs on | Ref | Token / variables visible | Key steps |
|---|---|---|---|---|---|
| `test` | test | MR + main | pipeline ref | `CI_JOB_TOKEN` (default scope); no deploy vars | `npm ci`, `npm test` (`allow_failure: true`, line 18) |
| `build` | build | MR + main | pipeline ref | `CI_REGISTRY_PASSWORD` | `docker build`, push `:$CI_COMMIT_SHA` and `:latest` |
| `deploy_prod` | deploy | main only (`rules: if $CI_COMMIT_BRANCH == "main"`, line 41) | main | `KUBE_CONFIG_PROD` (protected) | `helm upgrade --install billing-worker ./chart --set image.tag=$CI_COMMIT_SHA` (line 47), `scripts/smoke.sh` |

`deploy_prod` declares `needs: [build]` and `environment: production`
(lines 39-40) and `resource_group: production` (line 42).

## Findings

### P1 — Failing tests do not block deploy

- **File**: `.gitlab-ci.yml:18`
- **Evidence**: `test:` has `allow_failure: true`; `deploy_prod` has
  `needs: [build]` only.
- **Impact**: A red test stage is shown as a warning and `deploy_prod`
  runs anyway. The pipeline gates nothing.
- **Fix**:
  ```yaml
  test:
    allow_failure: false   # or delete the line
  deploy_prod:
    needs: [test, build]
  ```

### P1 — Migration runs after new pods roll out; upgrade is not atomic

- **File**: `chart/templates/migrate-job.yaml:5`, `.gitlab-ci.yml:47`
- **Evidence**: `"helm.sh/hook": post-upgrade`; the deploy command has no
  `--wait` or `--atomic`.
- **Impact**: Migration `20260914_add_invoice_currency.sql` adds
  `invoices.currency` (nullable, additive). New code in this release
  selects it, so new pods start before the column exists and fail until
  the hook finishes. If the hook fails, Helm marks the release failed but
  leaves new pods running against the old schema, and no rollback fires.
- **Fix**: run expand migrations before the rollout and make the upgrade
  roll back on failure:
  ```yaml
  # migrate-job.yaml
  "helm.sh/hook": pre-upgrade,pre-install
  "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
  ```
  ```bash
  helm upgrade --install billing-worker ./chart \
    --set image.tag="$CI_COMMIT_SHA" --wait --atomic --timeout 10m
  ```

### P2 — `:latest` tag pushed and used as chart default

- **File**: `.gitlab-ci.yml:29`, `chart/values.yaml:4`
- **Evidence**: `docker push $IMAGE:latest`; `image.tag: latest` with
  `pullPolicy: Always`.
- **Impact**: The pipeline overrides the tag, so prod is pinned. But anyone
  running `helm upgrade` by hand without `--set` deploys whatever `latest`
  is, and pods rescheduled from such a release can pull different code.
- **Fix**: remove the `:latest` push; set `image.tag: ""` and
  `{{ required "image.tag is required" .Values.image.tag }}` in the template.

### P2 — Smoke test failure is ignored

- **File**: `scripts/smoke.sh:1-9`
- **Evidence**: no `set -euo pipefail`; `curl -s` (no `-f`) followed by
  `echo "smoke ok"`.
- **Impact**: A 500 from `/healthz` still exits 0. The post-deploy gate
  exists on paper only.
- **Fix**: `set -euo pipefail` and `curl -fsS --retry 5 --retry-delay 3
  "$URL/healthz"`.

### P3 — Container runs as root

- **File**: `Dockerfile` (no `USER`), `chart/templates/deployment.yaml`
  (no `securityContext`)
- **Fix**: `USER node` in the Dockerfile; `runAsNonRoot: true`,
  `allowPrivilegeEscalation: false` in the pod spec.

## Checked and fine

- **Deploy branch restriction**: `deploy_prod` rules limit it to `main`;
  MR pipelines cannot reach it.
- **Concurrency**: `resource_group: production` serializes deploys, so two
  merges cannot roll out or migrate at once.
- **Base image**: `FROM node:20.17-bookworm-slim@sha256:...` is pinned by
  digest.
- **Readiness probe**: `deployment.yaml:31-36` gates traffic on
  `/healthz` with sensible thresholds; `maxUnavailable: 0`.
- **Migration is additive**: adding a nullable column is backward
  compatible with the running version; no expand/contract split needed.
  Only its position (post-upgrade) is wrong.
- **Credentials**: kubeconfig comes from a protected variable scoped to the
  `production` environment; no secrets echoed, written to artifacts, or
  baked into the image (`.dockerignore` excludes `.env*`).

## Required before enabling

1. Remove `allow_failure: true` from `test`; `deploy_prod` `needs: [test, build]`.
2. Move the migration hook to `pre-upgrade`; add `--wait --atomic --timeout`.
3. Make `smoke.sh` fail on HTTP errors.
4. Confirm `main` is protected and `KUBE_CONFIG_PROD` is protected + masked.
5. Document rollback: `helm rollback billing-worker <previous-revision>`
   (safe for this release because the migration is additive).

P2/P3 items can follow in the next change.
