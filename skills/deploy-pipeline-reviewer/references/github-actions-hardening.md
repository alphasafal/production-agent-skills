# GitHub Actions (and GitLab CI) hardening checklist

Use during the job-by-job trace. Each item says what to look for, why it
matters, and the fix. GitLab equivalents are noted where they differ.

## Triggers: who can make this run?

| Trigger | Runs with secrets? | Token | Code it should check out |
|---|---|---|---|
| `pull_request` (from fork) | No | read-only | PR head (safe: no secrets) |
| `pull_request` (same repo) | Yes | per `permissions` | PR head |
| `pull_request_target` | **Yes** | **write by default** | **Base ref only** |
| `workflow_run` | Yes | write | Never artifacts/code from the triggering run without validation |
| `issue_comment` | Yes | write | Anyone who can comment can trigger it |
| `push` | Yes | per `permissions` | The pushed ref |

- **The core rule**: untrusted code (PR head, fork artifacts, comment text)
  must never execute in a job that has secrets or a write token.
  `pull_request_target` + `actions/checkout` with
  `ref: ${{ github.event.pull_request.head.sha }}` (or `head.ref`, or
  `refs/pull/N/merge`) is P0. Executing includes `npm ci`/`pip install`
  (lifecycle scripts), test runners, Makefiles, Dockerfiles and local
  actions from the checkout.
- **Script injection**: `${{ github.event.pull_request.title }}`,
  `...head_ref`, `...comment.body`, `...issue.title` interpolated directly
  into `run:` are shell injection. Fix: pass through `env:` and quote
  (`TITLE: ${{ github.event.pull_request.title }}` then `"$TITLE"`).
- **Branch filters**: `branches: ["**"]` or no filter on a deploy workflow
  means every branch deploys. Restrict to `main`/release tags, and add an
  `if: github.ref == 'refs/heads/main'` on the deploy job as a second guard.
- GitLab: check `rules:`/`only:` on deploy jobs, and whether pipelines for
  merge requests from forks run in the parent project (they get protected
  variables only if the branch is protected).

## Permissions

- Set top-level `permissions: contents: read` (or `{}`), then grant per job.
  `write-all`, or no `permissions` key on an org whose default is
  read/write, gives every step push, release and PR-approval rights.
- OIDC deploys need `id-token: write` on the deploy job only.
- GitLab: `CI_JOB_TOKEN` scope and protected variables; deploy variables
  should be "protected" and "masked" and the deploy branch protected.

## Secrets handling

- Masking only redacts exact string matches in step logs. It does not
  cover: files (`env > file`, `.env` written to disk), artifacts, caches,
  Docker image layers, transformed values (base64, URL-encoded, substrings),
  or values sent to third-party services.
- Red patterns: `echo "$SECRET"`, `set -x` in scripts that use secrets,
  `env`/`printenv`/`export -p`, `cat ~/.aws/credentials`, uploading the
  workspace as an artifact, `docker build --build-arg SECRET=...`
  (persists in image history; use BuildKit `--secret`).
- Job-level `env:` exposes a secret to every step in the job, including
  third-party actions. Scope secrets to the single step that needs them.
- If a leak may already have happened (workflow ran, artifact exists):
  rotate, delete artifacts and logs, and audit cloud trail for the key.

## Cloud credentials: OIDC over static keys

- Static `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`, GCP JSON keys, Azure
  client secrets in repo secrets are long-lived and leak-prone.
- Fix (AWS): `aws-actions/configure-aws-credentials` with `role-to-assume`,
  `permissions: id-token: write`, and a trust policy whose `sub` condition
  is `repo:ORG/REPO:environment:production` (not `repo:ORG/REPO:*`).
  Equivalent: GCP Workload Identity Federation, Azure federated credentials,
  GitLab `id_tokens:`.

## Supply chain

- **Actions**: pin third-party actions to a full 40-char commit SHA with a
  version comment (`@<sha> # v4.2.2`). Branch refs (`@main`, `@master`) are
  P1 when the job has secrets: anyone with push to that repo runs code in
  your deploy. Tags (`@v4`) are mutable; lower risk for `actions/*` and
  major vendors, still worth pinning (P2). A SHA-pinned action is correct —
  do not flag it.
- **Installers**: `curl ... | bash`, `wget -O- | sh`, `pip install` from a
  URL, `go install ...@latest` in a job with secrets: P1. Fix: pinned
  version + checksum (`sha256sum -c`), signed release, or a pinned action.
- **Images**: `container:`/`services:` images and `docker run` with
  `:latest` or no digest.
- **Caches**: `actions/cache` or `setup-*` `cache:` written by a run that
  executed untrusted code can be restored by a trusted run (cache
  poisoning). Do not save caches from `pull_request_target` or fork-code
  jobs.
- Dependabot (or Renovate) for `github-actions` keeps SHA pins current.

## Gating and concurrency

- Deploy job must `needs:` the test (and build) job. Without `needs:`, jobs
  run in parallel and deploy ignores test results.
- Look for test bypasses: `continue-on-error: true`, `|| true`,
  `if: always()` on deploy, `workflow_dispatch` inputs like `skip_tests`,
  path filters that skip tests but not deploy.
- `environment: production` with required reviewers, wait timer and
  "deployment branches: selected" restricts who and what can deploy, and
  scopes prod secrets to that environment.
- `concurrency: { group: deploy-production, cancel-in-progress: false }`
  serializes deploys. `cancel-in-progress: true` on deploys can kill a
  half-applied migration — prefer `false` for deploy, `true` for CI.

## Fix snippet: minimal safe shape

```yaml
on:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<sha> # v4.x
      - run: npm ci && npm test
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    concurrency:
      group: deploy-production
      cancel-in-progress: false
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@<sha> # v4.x
      - uses: aws-actions/configure-aws-credentials@<sha> # v4.x
        with:
          role-to-assume: ${{ vars.DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
```
