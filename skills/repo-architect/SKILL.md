---
name: repo-architect
description: >
  Builds a structured map of an unfamiliar repository — entry points, modules,
  dependencies, data flow, persistence, external integrations, and architectural
  risks — before any code is changed. Use when starting work in a codebase you
  haven't worked in before, onboarding to a new repo, preparing to plan a
  non-trivial change, or when asked to "understand this codebase", "explain the
  architecture", "map how the existing system works", document a codebase's
  module structure and dependencies, or assess the overall health of an entire
  codebase. Do not use for a codebase you already understand well, for a single
  well-scoped file edit, or as a substitute for actually implementing a change
  (it produces a map, not a fix).
license: MIT
compatibility: Needs filesystem read access to the repository. No network required.
metadata:
  category: engineering
  composes_with:
    - feature-to-production
    - system-design-reviewer
---

# Purpose

Produce a reliable mental model of a repository's structure, boundaries, and
risks before changing anything in it — so later changes are informed rather
than exploratory.

# When to use

- First time working in a repo, or a part of it you haven't touched.
- Preparing to plan a feature or refactor and need to know what exists.
- Asked directly to explain, document, or map a codebase's architecture.

# When NOT to use

- You (the agent) already have a solid working model of this exact repo from
  earlier in the session — don't re-map it.
- The task is a small, well-scoped edit to a file you can read directly.

# Required inputs

- Read access to the repository root.

# Workflow

**Do not modify any code during this workflow.** The output is a map, not a
change. If the user's real goal is a change, finish this investigation first,
then hand off to a change-making skill (e.g. `feature-to-production`) or ask
before editing.

1. **Identify repository boundaries** — is this one project, a monorepo with
   multiple packages/services, or a repo embedding vendored/generated code
   that shouldn't be treated as first-party? Check for workspace configs
   (`pnpm-workspace.yaml`, `lerna.json`, `go.work`, multiple `pyproject.toml`).
2. **Detect languages/frameworks** — from manifest files (`package.json`,
   `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`) and lockfiles, not
   from guessing off file extensions alone.
3. **Find entry points** — where execution starts: `main`, HTTP route
   registration, CLI command definitions, cron/worker entry files, exported
   library API surface.
4. **Map modules** — the top-level organization (by feature? by layer? by
   package?) and what each major directory is responsible for.
5. **Map dependencies** — both internal (which modules import which) and
   external (key third-party libraries and what role they play — web
   framework, ORM, queue client, etc). Flag any dependency doing something
   architecturally significant (auth, payments, data validation at the boundary).
6. **Understand data flow** — how a request/job/event moves through the
   system from entry point to response/side effect.
7. **Understand persistence** — what's stored, where (which database(s),
   cache(s), object storage), and how schema/migrations are managed.
8. **Understand external integrations** — third-party APIs, webhooks,
   message queues, other internal services this repo talks to.
9. **Identify architectural boundaries** — where are the seams? (e.g.
   API layer vs. domain logic vs. persistence; service-to-service contracts
   in a monorepo). Are they enforced (module boundaries, lint rules) or just
   conventional?
10. **Identify risks/unknowns** — undocumented behavior, missing tests around
    critical paths, unclear ownership, deprecated-looking code still in the
    critical path, version-mismatched dependencies.
11. **Generate the structured repository map** — write the output contract
    below. This is the deliverable of this skill.

# Tool & resource guidance

- If the repo looks like a frontend app (React/Vue/Next/etc.), read
  `references/frontend-architectures.md` before mapping modules.
- If it looks like a backend service, read `references/backend-architectures.md`.
- If you found multiple workspace packages/services in step 1, read
  `references/monorepos.md` before mapping dependencies.
- If services communicate over the network with each other (not just to
  third-party APIs), read `references/distributed-systems.md`.
- For unfamiliar directory layouts, `references/common-project-structures.md`
  has patterns to check against per language/framework.
- Prefer reading manifest/config files and following actual imports over
  inferring structure from directory names alone.

# Output contract

Produce these files (or equivalent structured sections if file output isn't
available in the environment):

- **ARCHITECTURE.md** — narrative overview: what the system is, its major
  components, request/data flow, and how it's deployed if determinable.
- **MODULE_MAP.md** — a directory-by-directory breakdown of responsibilities.
- **DEPENDENCY_MAP.md** — internal module dependencies and key external
  libraries with their architectural role.
- **RISK_REGISTER.md** — a list of risks/unknowns found, each with what's
  unclear and why it matters for future changes.

# Quality checks

- [ ] Every claim about structure is backed by an actual file/import read,
      not inferred from naming conventions alone.
- [ ] Entry points are named specifically (file + function/route), not vague.
- [ ] The risk register names concrete unknowns, not generic boilerplate
      ("tests could be better") — each item should be actionable.
- [ ] No code was modified during this investigation.

# Red flags

Stop and correct course if any of these are true:

- You have edited, created, or deleted a file in the repository being mapped.
- The tech stack in your map came from file extensions, not manifest or lockfiles.
- Your data-flow description doesn't name a real entry point (route, CLI command, worker, `main`).
- Vendored or generated code is described as first-party architecture.
- The map states how something works with no file path behind it.
- The risks section is empty.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "I'll just fix this small thing I noticed while mapping." | This skill's output is a map, not a change. Note it as a risk; edits belong to a change-making skill, after the map exists. |
| "The README explains the architecture already." | READMEs drift. Treat it as a claim to verify against entry points and imports, and flag where they disagree. |
| "It's a standard Next.js / Django app, I know the layout." | Frameworks set defaults; teams override them. Check the actual structure before describing it. |
| "No risks jumped out." | Every real repo has untested critical paths, unclear ownership, or stale dependencies. Absence means you haven't looked yet. |
| "Mapping everything would take too long; I'll describe the top-level folders." | A folder list isn't a map. Follow at least one request from entry point to persistence — that's what makes the map useful. |

# Edge cases

- **Monorepo with unrelated packages**: scope the map to the package(s)
  relevant to the user's actual goal, and note the rest exists without
  fully mapping it — read `references/monorepos.md`.
- **Repo has little/no documentation and unclear ownership**: say so in the
  risk register explicitly rather than presenting inferred structure as
  confirmed fact.
- **Generated/vendored code present**: identify and exclude it from the
  module map, noting where it's vendored from.
- **Repository is too large to fully map in one pass**: map the boundaries
  and entry points fully, then go deep only on the area relevant to the
  user's stated goal — say explicitly what was scoped out.
- **The repo is a library/framework, not an application**: there is no
  `main`, no served route, and no request flow to trace. Map the
  **exported public API surface** as the entry point instead, and treat
  "no `cmd/` directory" or "no `main` field" as expected rather than as a
  finding. Read `references/common-project-structures.md` first — its
  opening section covers how to tell the two apart.

# References

See `examples/` for worked examples of this skill's output on a Next.js app
(`nextjs-repository.md`), a Python service (`python-service.md`), a Go
backend (`go-backend.md`), and a monorepo (`monorepo.md`).
