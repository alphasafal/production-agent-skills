# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] — 2026-10-21

### Added

- **Anti-shortcut guardrails in every skill.** New required `# Red flags`
  and `# Common rationalizations` sections: observable signs the workflow
  is being skipped, and the excuses agents use to skip it with why they
  don't hold. Enforced by `validate_skills.py` (≥3 of each, standard order).
- **Catalog-wide routing eval** (`scripts/run_routing_evals.py`, CI-gated):
  BM25 over every skill's name and positive description. Gates obvious
  prompts at rank #1 of all skills, ambiguous prompts in the top 3,
  cross-routing negatives (new `route_to` field) and description
  collisions. Reports a held-out prompt set (`evaluations/routing/`) that
  is never used for tuning.
- **Behavioral eval runner** (`scripts/run_behavioral_evals.py`): runs each
  workflow scenario with and without the skill through headless Claude
  Code in isolated workspaces, blind-graded by a separate call; plus an
  activation mode that measures which skill a real agent loads.
- **Pressure scenarios** (`evaluations/workflows/pressure/`, 5): time
  pressure, authority, sunk cost, skip-the-tests, CEO scope.
- **First real benchmark** in `evaluations/results/README.md`.
- **Claude Code plugin + marketplace manifests** and 8 slash commands
  (`/investigate`, `/pr-review`, `/map-repo`, `/design-review`,
  `/analyze-data`, `/decide`, `/prd`, `/ship-feature`). Validated with
  `claude plugin validate`.
- `schemas/workflow.schema.json`; workflow scenarios now declare
  `workspace_files` (agent sees) and `reference_answer` (grader only), and
  the validator rejects any scenario that would leak an answer or spoiler.
- `evaluations/fixtures/public-api/`, a small stdlib API with tests, so the
  feature-to-production scenario has a real codebase to change.
- CI: routing gate, behavioral dry-run, and an 8,000-char discovery-budget
  check via `skills-ref to-prompt`.

### Changed

- All 8 descriptions widened with the vocabulary users actually use
  ("throws", "OOM", "logged out", "vendor", "will this scale", "CSV"…).
  Obvious-prompt routing went from 32/40 to 40/40 at rank #1; "Do not
  use…" guidance kept intact.
- The debugging scenario now runs against the runnable sample app instead
  of a diff, and the repo-architect scenario against a real codebase.
- `feature-to-production`: new red flag and rationalization for skipping
  the review stage. Added after the behavioral eval showed the agent
  skipping it even with the skill loaded.

## [0.1.0] — 2026-09-12

### Added

- Eight flagship skills: `repo-architect`, `debugging-investigator`,
  `production-code-review`, `system-design-reviewer`, `data-scientist`,
  `research-to-decision`, `product-manager`, `feature-to-production` —
  each with a `SKILL.md`, references, examples, and (where relevant)
  bundled deterministic scripts or asset templates.
- Static validation tooling (`scripts/validate_skills.py`,
  `scripts/inspect_skill.py`, `scripts/list_skills.py`,
  `scripts/run_static_evals.py`) and a portable installer
  (`scripts/install_skills.py`).
- Two JSON Schemas (`schemas/skill-manifest.schema.json`,
  `schemas/evaluation.schema.json`) making "valid skill" and "valid eval
  case" mechanically checkable.
- 80 activation evaluation cases (10 per skill) and 8 workflow evaluation
  scenarios, plus the fixtures they reference.
- 13 conceptual/reference docs under `docs/`, client compatibility notes
  for Claude Code, OpenAI Codex, and GitHub Copilot under `clients/`, and
  a runnable buggy sample app under `examples/02-debug-a-failure/`.
- GitHub Actions CI (`.github/workflows/validate-skills.yml`) running the
  full pytest suite and static validation on every push/PR.

### Verified

- All 8 skills validate against `skills-ref`, the reference implementation
  of the open spec — enforced per-skill in CI.
- Full test suite green on Python 3.9, 3.11, and 3.13 (CI matrix), matching
  the declared `requires-python = ">=3.9"`.
- Bundled `data-scientist` scripts checked against a real 891-row public
  dataset, with outputs matched to independently-computed ground truth.
- `examples/02-debug-a-failure` bug confirmed to reproduce 10/10 runs, with
  the documented fix resolving it and the regression test failing pre-fix
  and passing post-fix.

### Fixed during verification

- Frontmatter used flow-style YAML lists (`[a, b]`), which the spec's
  strict parser rejects — all 8 skills failed the official validator.
  Converted to block style and added `strict_yaml_violations()` plus
  `tests/test_spec_strictness.py` so it cannot regress.
- `install_skills.py` created the target directory before validating the
  skill name, leaving an empty directory behind on a typo.
- `check_missingness.py` printed an empty "Co-occurrence" header when no
  columns had correlated missingness.
- `data-scientist` scripts raised a raw `ModuleNotFoundError` traceback
  instead of a readable install hint when pandas/numpy were absent.
- `repo-architect` reference material assumed application layouts and would
  have mislead an agent mapping a library (no `cmd/` in Go libraries, Python
  `src/` layouts, Node packages with no `main` field).

### Status

`evaluations/results/README.md` is intentionally unfilled
(`NOT YET BENCHMARKED`) — no real before/after activation or workflow
numbers have been recorded yet. See `docs/evaluating-skills.md` for the
methodology.
