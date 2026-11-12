# Security

## Trust model

Skills in this repository can bundle scripts (see `skills/data-scientist/scripts/`)
that an agent will execute on your behalf. **Read a skill before running its
bundled scripts, especially from a fork or a third-party skill you didn't
author** — a `SKILL.md` is instructions an agent follows, and a `scripts/`
file is code that actually runs. Both deserve the same scrutiny you'd give
any other code you're about to execute.

## What this repo's own scripts do and don't do

- No script in this repository collects credentials or sends anything
  anywhere, and none performs a destructive filesystem operation (delete,
  overwrite) unless you pass `--force` or `--uninstall`.
- `install.sh` makes exactly one network request: it downloads this
  repository's source archive from `codeload.github.com`. It then copies the
  skills you selected into the skills directory, deletes its temporary
  download, and exits. It does not use `sudo`, does not edit shell profiles
  or agent settings, and does not run any code from the download.
- `scripts/install_skills.py` and `install.sh` never overwrite an existing
  installation without `--force`, only uninstall a directory that contains a
  `SKILL.md`, and support `--dry-run` to preview any change before it
  happens.
- `skills/data-scientist/scripts/*.py` only read the dataset file(s) you
  pass on the command line and print results — they don't write, delete,
  or transmit anything.
- No script shells out with unsanitized string interpolation; where
  external tools are invoked (`scripts/validate_skills.py`'s optional
  `skills-ref` integration), arguments are passed as a list, never through
  a shell string.

## Installing without trusting a pipe

`curl ... | sh` runs whatever the URL returns at that moment. If you would
rather not:

- **Read it first.** `install.sh` is one short file with no dependencies:
  `curl -fsSLO https://raw.githubusercontent.com/alphasafal/production-agent-skills/main/install.sh`,
  open it, then `sh install.sh --pack <role>`.
- **Pin a version.** `--ref v0.4.0` installs that tag's skills instead of
  whatever `main` is today.
- **Skip the script.** Download a `pack-<role>.zip` from a
  [release](https://github.com/alphasafal/production-agent-skills/releases),
  compare it with `SHA256SUMS` from the same release
  (`sha256sum -c SHA256SUMS --ignore-missing`), and unzip it into your
  skills directory. The archives are built by
  `.github/workflows/release.yml` from the tagged commit.

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
