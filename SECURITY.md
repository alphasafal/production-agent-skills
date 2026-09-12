# Security

## Trust model

Skills in this repository can bundle scripts (see `skills/data-scientist/scripts/`)
that an agent will execute on your behalf. **Read a skill before running its
bundled scripts, especially from a fork or a third-party skill you didn't
author** — a `SKILL.md` is instructions an agent follows, and a `scripts/`
file is code that actually runs. Both deserve the same scrutiny you'd give
any other code you're about to execute.

## What this repo's own scripts do and don't do

- No script in this repository collects credentials, makes network calls,
  or performs destructive filesystem operations (delete, overwrite outside
  an explicit `--force`/`--target`) by default.
- `scripts/install_skills.py` never overwrites an existing installation
  without `--force`, and supports `--dry-run` to preview any change before
  it happens.
- `skills/data-scientist/scripts/*.py` only read the dataset file(s) you
  pass on the command line and print results — they don't write, delete,
  or transmit anything.
- No script shells out with unsanitized string interpolation; where
  external tools are invoked (`scripts/validate_skills.py`'s optional
  `skills-ref` integration), arguments are passed as a list, never through
  a shell string.

## Reporting a vulnerability

If you find a security issue in this repository's tooling (not in a
third-party client that happens to run these skills), please open a
GitHub issue with the `security` label, or contact the maintainer
directly if the issue is sensitive enough that public disclosure before a
fix would be harmful. There is no bug bounty program for this project.

## Scope

This policy covers the code and skills in this repository. It does not
cover the security posture of any client (Claude Code, Codex, Copilot,
etc.) that runs these skills — report issues in those tools to their
respective maintainers.
