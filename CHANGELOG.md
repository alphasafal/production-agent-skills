# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] — Unreleased

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

### Status

`evaluations/results/README.md` is intentionally unfilled
(`NOT YET BENCHMARKED`) — no real before/after activation or workflow
numbers have been recorded yet. See `docs/evaluating-skills.md` for the
methodology.
