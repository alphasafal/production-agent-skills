# Architecture

## Design principle: one canonical source of truth

Every skill lives once, at `skills/<name>/`, in the plain open Agent
Skills format (`clients/generic-agent-skills.md`). There is no
`skills-claude/`, `skills-codex/`, etc. — client-specific behavior lives in
`clients/*.md` (documentation) and `scripts/install_skills.py` (an
adapter that copies the canonical folder to wherever a client reads
skills from), never as a fork of the skill's actual instructions. See
`docs/skill-anatomy.md` for why this is even possible: the frontmatter
this repo uses (`name`, `description`, `license`, `allowed-tools`,
`compatibility`, `metadata`) is the open spec's field set, not any one
vendor's extensions.

## Repository layout and why

```
skills/          the 8 canonical skills — the actual product
evaluations/     proof the skills behave as specified (activation + workflow)
examples/        end-to-end walkthroughs, one per skill, for humans reading the repo
docs/            conceptual + reference documentation
clients/         per-client compatibility notes and verified install paths
scripts/         tooling: validate, inspect, list, install, run static evals
tests/           pytest suite over the tooling's guarantees
schemas/         the two JSON Schemas that make "valid skill"/"valid eval case" checkable
demos/           material for recording a walkthrough video
```

`skills/` and `evaluations/` are the load-bearing directories; everything
else exists to make `skills/` trustworthy (tests, schemas, scripts) or
understandable (docs, examples, clients).

## Tooling design

`scripts/_lib.py` is the one shared internal module — it parses
`SKILL.md` frontmatter, discovers skills, and extracts relative-path
references from a skill's body. Every other script (`validate_skills.py`,
`inspect_skill.py`, `list_skills.py`, `run_static_evals.py`,
`install_skills.py`) and every test in `tests/` imports it, so "what
counts as a skill" and "how do we parse one" is defined exactly once.

This is a deliberate exception to the "no shared framework" rule this repo
otherwise follows — the *skills themselves* (especially
`data-scientist`'s bundled scripts) are kept standalone and independently
runnable on purpose, since a user might copy a single script out of a
skill folder; but the top-level tooling that operates *on* the skills repo
as a whole is normal internal infrastructure, and sharing it there avoids
eight slightly-different reimplementations of "parse YAML frontmatter."

## Validation pipeline

`scripts/validate_skills.py` is the single static gate. It checks, per
skill: frontmatter schema compliance, name/directory match, description
quality heuristics, body length (progressive-disclosure discipline),
every relative reference in the body actually resolving to a real file,
scripts declaring their third-party dependencies, no empty directories,
and (per skill) a matching `evaluations/activation/<name>.json` that
itself validates against `schemas/evaluation.schema.json` with minimum
category coverage. It optionally shells out to the community `skills-ref`
CLI if installed, and degrades gracefully (a warning, not a failure) if
that CLI isn't present — see `.github/workflows/validate-skills.yml`.

`tests/` mirrors most of the same checks as pytest assertions, so
`pytest` and `validate_skills.py` can both act as a CI gate; they're kept
in sync by both importing the same discovery logic from `_lib.py` rather
than each re-implementing skill discovery.

## Evaluation framework design

Two tiers, deliberately kept separate because they answer different
questions and need different kinds of checking:

- `evaluations/activation/*.json` — 10 short, structurally-validated cases
  per skill (5 obvious positive, 2 ambiguous positive, 3 negative). Fully
  machine-checkable for shape; `scripts/run_static_evals.py` adds a
  lexical-overlap heuristic as a *hint*, not a verdict — it explicitly
  does not call a model or claim to measure real activation accuracy.
- `evaluations/workflows/*.json` — one deeper scenario per skill, with a
  fixture (`evaluations/fixtures/`) and a set of required/forbidden
  behaviors meant for a human or LLM-judge to grade a real transcript
  against. These are intentionally not auto-graded — grading "did the
  agent correctly identify the concurrency race as the root cause" isn't
  a schema-checkable property.

See `docs/evaluating-skills.md` for the full before/after methodology and
`evaluations/results/README.md` for why every number in this repo is
currently `NOT YET BENCHMARKED` rather than invented.

## Installer design

`scripts/install_skills.py` copies whole skill directories
(`shutil.copytree`, pathlib throughout, no shell-outs) into a
caller-specified target — never a hard-coded "correct" path, since no such
universal path exists across clients (see `clients/README.md`). It
refuses to silently overwrite an existing install (`--force` required),
supports `--dry-run`, and excludes `__pycache__`/`.pyc` artifacts from the
copy. `tests/test_installer.py` exercises all of this against a temp
directory rather than the real filesystem locations a user would target.
