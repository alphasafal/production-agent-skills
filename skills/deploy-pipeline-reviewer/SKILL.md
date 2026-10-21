---
name: deploy-pipeline-reviewer
description: >
  Reviews deployment pipelines and release config before they are turned on
  or changed: inventory, trace of triggers, refs, permissions and secrets,
  supply chain, test gating, deploy safety, migration ordering, concurrency,
  then ranked P0-P3 findings with fixes and a go/no-go. Use when asked to
  review, audit or harden a GitHub Actions or GitLab workflow, a
  pull_request_target trigger, Dockerfile, deploy script, Kubernetes or Helm
  manifest, Terraform plan, or migration rollout — "is this pipeline safe to
  turn on", "check our deploy workflow", "could this leak secrets". Do not
  use for reviewing an application code diff (use production-code-review), or
  building and shipping a feature (use feature-to-production).
license: MIT
compatibility: Needs read access to the workflow, container, deploy-script, manifest, IaC and migration files. No network or cloud access required.
metadata:
  category: devops
  composes_with:
    - production-code-review
    - feature-to-production
---

# Purpose

Catch the ways a pipeline hurts production before it runs: leaked or
over-scoped credentials, untrusted code executing with secrets, deploys that
skip tests or approval, migrations that break the version still serving
traffic, and releases nobody can roll back. Judge what the pipeline will
actually do when triggered, not whether the YAML parses.

# When to use

- A new or changed CI/CD workflow (GitHub Actions, GitLab CI, CircleCI,
  Jenkinsfile) is about to be enabled, merged, or pointed at production.
- A Dockerfile, deploy script, Kubernetes/Helm manifest, or Terraform/IaC
  change alters how or where code ships.
- A release includes a schema migration and the question is ordering,
  reversibility, or rollback.
- Asked "is this pipeline safe", "harden our CI", or "review our deploy setup".

# When NOT to use

- The change is application logic (a handler, a query, a UI) with no
  pipeline or deploy config involved — use `production-code-review`.
- The task is to build and ship a feature end to end — use
  `feature-to-production`; it calls this skill if pipeline config changes.
- Auditing application code for vulnerabilities (injection, auth bugs) is a
  security audit of the app (e.g. `security-auditor`), not a pipeline review.
- Debugging a pipeline that is already failing — that is an investigation.

# Required inputs

- Every workflow file that can reach production, plus the scripts,
  Dockerfiles, manifests and IaC they invoke. A workflow that calls
  `./deploy.sh` is not reviewed until `deploy.sh` is read.
- Migrations shipping in the same release and a note of what code reads the
  affected tables (CHANGELOG, diff, or the data-access module).
- If missing: branch protection and environment settings are not in the repo.
  State them as assumptions ("assumes no required reviewers on `production`")
  rather than assuming the safe setting.

# Workflow

1. **Inventory.** List every pipeline file and everything it executes:
   workflows, called scripts, Dockerfiles, manifests, IaC, migrations,
   third-party actions/orbs/images. Anything referenced but not read goes on
   a "not reviewed" list in the report.
2. **Map triggers.** For each workflow record `on:` events, branch/tag
   filters, and whether it runs for forks (`pull_request_target`,
   `workflow_run`, `issue_comment`). Note who can cause each run.
3. **Trace job by job.** For each job and step write down: the code it
   checks out (which ref), the token permissions in effect, the secrets and
   env vars visible, and what runs (`run:`, actions, installers). The
   dangerous combination is untrusted code + secrets or a write token.
4. **Supply chain.** Check pinning of actions (full SHA vs tag vs branch),
   base images (`:latest`, no digest), `curl | bash` and unverified
   downloads, unpinned tool versions, caches written by untrusted runs.
5. **Secrets and permissions.** Find secrets echoed, `set -x` near secrets,
   `env`/`printenv` dumps, secrets written to files, artifacts, images or
   caches; `permissions: write-all` or missing top-level `permissions`;
   long-lived cloud keys where OIDC is available.
6. **Gating.** Confirm the deploy job `needs:` the test job, that tests
   cannot be skipped (`continue-on-error`, `|| true`, path filters, manual
   input flags), and that prod deploys are restricted to the release branch
   or tag.
7. **Deploy safety.** Look for `environment:` protection with reviewers,
   a health/readiness gate after deploy, progressive rollout (canary, rolling
   with max-unavailable, circuit breaker), and an automated or documented
   rollback. Read deploy scripts for `set -euo pipefail` and exit codes.
8. **Migrations.** For each migration: additive or destructive? Does it run
   before or after new code is live? Can the previous version still run
   against the new schema during rollout and after a rollback? Destructive
   changes need expand/contract across separate releases.
9. **Concurrency and reproducibility.** Check for a `concurrency:` group
   on deploy jobs, overlapping migrations, and whether a rebuild of the
   same commit produces the same artifact.
10. **Check suspicious-looking config before flagging it.** For each
    candidate, confirm it is actually exploitable or harmful in this repo
    (e.g. `pull_request` + `contents: read` with no secrets is fine). Drop
    or downgrade what is not.
11. **Rank and fix.** Assign P0-P3, attach file:line, evidence, impact and
    a concrete fix snippet. Give a go/no-go with the ordered list of what
    must change first, and say whether any exposed secret must be rotated.

## Severity rubric

- **P0**: secrets exposed or reachable by untrusted code, prod writable by
  anyone who can open a PR, or an irreversible data change during rollout.
  Blocks enabling.
- **P1**: prod deploy without test gating, branch restriction or approval;
  no rollback; unverified code executing with secrets. Blocks enabling
  unless explicitly accepted by an owner.
- **P2**: bounded risk — tag-pinned first-party actions, missing
  concurrency, `:latest` images, root containers, missing health check
  where a platform circuit breaker exists.
- **P3**: hygiene — caching, image size, naming, log noise.

# Tool & resource guidance

- For any GitHub Actions or GitLab CI workflow, read
  `references/github-actions-hardening.md` before step 3.
- If a release contains a schema migration, or the pipeline has no rollback
  or health check, read `references/migrations-and-rollout.md`.
- If the change includes a Dockerfile, Kubernetes/Helm manifest, or
  Terraform, read `references/containers-and-iac.md`.
- Use grep across the repo for `secrets.`, `pull_request_target`,
  `permissions`, `curl`, `| bash`, `:latest`, `DROP`, `needs:`. Grep finds
  candidates; the job trace decides whether they matter.

# Output contract

Write `PIPELINE_REVIEW.md` with these sections, in order:

1. **Verdict** — GO, GO WITH CONDITIONS, or NO-GO, plus a one-line reason.
2. **Scope** — files reviewed, files referenced but not reviewed, and
   stated assumptions about repo/environment settings.
3. **Pipeline trace** — per workflow: triggers, then per job the ref
   checked out, token permissions, secrets visible, and key steps.
4. **Findings** — ranked P0 first. Each: severity, file:line, evidence
   (quoted config), impact, fix (a YAML/shell/SQL snippet).
5. **Checked and fine** — items that look risky but are correctly
   configured, with one line on why.
6. **Required before enabling** — ordered checklist, including secret
   rotation if credentials may already have leaked.

# Quality checks

- [ ] Every workflow job has a trace entry naming its ref, permissions and secrets.
- [ ] Every finding has file:line, quoted evidence and a fix snippet.
- [ ] Every migration is classified additive/destructive with its run
      position relative to the deploy step.
- [ ] Each "Checked and fine" item states why it is safe, not just that it is.
- [ ] The verdict matches the findings: no GO with an open P0 or P1.
- [ ] Scripts invoked by the pipeline were read, not inferred from their names.

# Red flags

- You are writing a verdict and the trace section has jobs with no
  permissions or secrets listed.
- A finding says "consider pinning" or "might leak" with no file:line.
- You called a job "CI only" or "just tests" without checking which
  secrets and token scope it has.
- Your findings are indentation, naming or deprecated-syntax comments while
  the trigger and checkout ref of the deploy job are unexamined.
- `deploy.sh` (or any invoked script) is in the workflow but you have not
  opened it.
- You flagged every `uses:` line identically, SHA-pinned ones included.
- A migration is in the release and you have not said whether old code
  still runs against the new schema.

# Common rationalizations

Excuses that show up when reviewing pipelines under time pressure:

| Rationalization | Reality |
|---|---|
| "It's only CI, it doesn't touch prod." | If the job can read a secret or a write token, it touches prod. Check the trace, not the job name. |
| "GitHub masks secrets in logs, so the echo is harmless." | Masking covers exact log matches only. Files, artifacts, base64 and substrings are not masked. |
| "`pull_request_target` is fine, we need secrets for PR previews." | It is fine only if PR head code never runs in it. Checking out the head ref hands secrets to any fork. |
| "The column is unused now, dropping it is safe." | Unused by the new version. The old version is still serving during rollout and is your rollback target. |
| "We'll add approvals and rollback after the first deploy." | The first deploy of a new pipeline is the one most likely to go wrong. Gate it before it runs. |
| "The YAML validates and the dry run passed." | Syntax and a happy path say nothing about who can trigger it or what secrets untrusted code sees. |

# Edge cases

- **Repo settings not visible** (branch protection, environment reviewers,
  OIDC trust policy): list them as assumptions and make the verdict
  conditional on them, rather than assuming either way.
- **Reusable workflows or composite actions**: trace into them; secrets
  passed with `secrets: inherit` are visible to the callee.
- **Self-hosted runners**: untrusted PR code on a persistent runner can
  persist malware between jobs — treat as P0 if forks can trigger it.
- **Monorepo path filters**: confirm a change to shared code cannot skip
  the tests that cover it while still deploying.
- **Already enabled and has run**: any exposure finding becomes "rotate
  now" in the required list, not just "fix the config".
- **Platform-managed deploys** (Vercel, Heroku, Argo CD): review the
  platform config file and promotion rules in place of a deploy script.

# References

- `references/github-actions-hardening.md` — triggers, permissions,
  pinning, secrets handling, OIDC, cache poisoning.
- `references/migrations-and-rollout.md` — expand/contract, migration
  ordering, health gates, progressive rollout, rollback.
- `references/containers-and-iac.md` — Dockerfile, Kubernetes/Helm and
  Terraform review points.
- `examples/gitlab-helm-review.md` — a full worked `PIPELINE_REVIEW.md`.
