# Containers, Kubernetes/Helm and Terraform review points

## Dockerfile

| Check | Finding if violated | Fix |
|---|---|---|
| Base image pinned | `FROM node:latest` / no tag / tag without digest: non-reproducible, silent major upgrades (P2) | `FROM node:20.17-slim@sha256:<digest>` |
| No secrets in build context or layers | `COPY .env`, `COPY . .` with no `.dockerignore`, `ARG`/`ENV` holding a token, `RUN echo $TOKEN > ~/.npmrc` (P0/P1 — anyone who can pull the image gets the secret; deleting in a later layer does not remove it) | `.dockerignore` with `.env`, `.git`, keys; BuildKit `RUN --mount=type=secret`; runtime injection (ECS secrets, K8s Secret, SSM) |
| Non-root | No `USER` → runs as root (P2) | `USER node` / numeric UID; `readOnlyRootFilesystem` in K8s |
| Reproducible deps | `npm install`, `pip install` without lock, `apt-get install` unpinned (P2/P3) | `npm ci --omit=dev`, lockfiles, pinned packages |
| Multi-stage | Build tools and dev deps in runtime image (P3) | Separate build and runtime stages |
| Remote fetch | `ADD https://...` or `curl | sh` during build (P1 if unverified) | Pinned URL + checksum |

## Kubernetes / Helm

- **Image**: `image: app:latest` or `imagePullPolicy: Always` with a mutable
  tag means two pods in one Deployment can run different code. Use an
  immutable tag (commit SHA) or digest.
- **Probes**: no `readinessProbe` → traffic hits pods before they are
  ready; rolling update can take the service down. No `livenessProbe` is
  lower severity. Probes pointing at a path that does not exist cause crash
  loops.
- **Rollout strategy**: `maxUnavailable` should be 0 (or low) for critical
  services; `minReadySeconds` and `progressDeadlineSeconds` set; a
  PodDisruptionBudget for multi-replica services; `replicas: 1` means every
  deploy is downtime.
- **Security context**: `privileged: true`, `hostNetwork`, `hostPath`
  mounts, `runAsUser: 0`, `allowPrivilegeEscalation` not false, added
  capabilities.
- **Secrets**: Secret values committed in `values.yaml` or manifests
  (base64 is not encryption). Use External Secrets / Sealed Secrets / SOPS.
- **Resources**: no requests/limits → noisy-neighbour evictions; not a
  deploy-safety P0, usually P2.
- **Helm**: `helm upgrade --install --wait --atomic --timeout` so a failed
  release rolls back; without `--atomic` a failed upgrade leaves a broken
  release. Check `helm diff` is run in CI for review.
- **Jobs/hooks**: migration as a `pre-upgrade` hook is the expand position;
  `post-upgrade` hooks are the contract position — same rules as
  `migrations-and-rollout.md`.

## Terraform / IaC

- **Plan before apply**: pipeline must run `terraform plan -out=tfplan`,
  have the plan reviewed (PR comment or approval), then `apply tfplan`.
  `apply -auto-approve` without a reviewed plan on prod is P1.
- **Destroy/replace**: scan the plan for `-/+` (replace) and `-` (destroy)
  on stateful resources (databases, buckets, volumes, DNS). Look for
  missing `lifecycle { prevent_destroy = true }`, `deletion_protection`,
  `skip_final_snapshot = true` on RDS.
- **State**: remote backend with locking (S3 + DynamoDB, GCS, Terraform
  Cloud); state is sensitive (contains secrets) — not uploaded as an
  artifact, bucket not public.
- **Providers and modules**: version-pinned (`required_providers` with
  constraints, `.terraform.lock.hcl` committed); modules from git pinned to
  a tag or SHA, not a branch.
- **Credentials**: OIDC to the cloud, scoped role per environment; plan
  role read-only, apply role gated by environment approval.
- **Blast radius**: one state for all environments means a dev change can
  touch prod; prefer per-environment state/workspaces.
- **Secrets in code**: passwords in `.tf` / `.tfvars`; use a secrets
  manager data source or generated passwords stored in the secret store.
