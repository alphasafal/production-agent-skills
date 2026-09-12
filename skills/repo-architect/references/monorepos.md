# Monorepo Mapping

## Identify the workspace tool first

The workspace manager determines how packages actually depend on each other
in practice (vs. what directory names suggest):

- **JS/TS**: `pnpm-workspace.yaml`, `package.json` `workspaces` field,
  `nx.json`, `turbo.json`, `lerna.json`.
- **Go**: `go.work` listing multiple modules.
- **Python**: multiple `pyproject.toml`/`setup.py` under one root, often
  with a tool like `uv workspace` or `poetry` path dependencies.
- **Polyglot**: `Bazel` (`BUILD`/`WORKSPACE`), `buck2`, or a custom root
  `Makefile`/`justfile` orchestrating per-package builds.

## What to map differently than a single-package repo

- **Package boundaries**: list each package/app with its own purpose —
  don't treat the monorepo as one flat module space.
- **Internal dependency graph between packages**: which apps depend on
  which shared libraries. This is often more important than any single
  package's internal structure, since a change to a shared package can
  ripple across many apps.
- **Versioning/publishing model**: are internal packages versioned
  independently (changesets, semantic-release per package) or always moved
  together? This affects how risky a shared-package change is.
- **Build/task orchestration**: does the task runner (Nx, Turborepo, Bazel)
  understand the dependency graph well enough to only rebuild/retest
  affected packages? If not, note that as a risk (changes may not be safely
  isolated in CI).

## Scoping the investigation

Don't fully map every package in a large monorepo. Map:
1. The dependency graph at the package level (fast, high-value).
2. Full internal structure only for the package(s) relevant to the actual task.
State explicitly which packages were scoped out.
