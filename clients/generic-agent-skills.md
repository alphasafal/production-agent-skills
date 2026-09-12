# Generic Agent Skills (open spec)

This repository's skills are written against the open Agent Skills
specification maintained at [agentskills.io](https://agentskills.io), not
against any single vendor's dialect. This doc covers what's true for any
compliant client; see the other files in this directory for
client-specific paths and behavior.

## Status

**Open standard**, originally developed by Anthropic, released publicly,
and adopted by 40+ agent products (Claude Code, OpenAI Codex/ChatGPT,
GitHub Copilot, Cursor, OpenCode, Gemini CLI, and others — see
[agentskills.io/clients](https://agentskills.io) for the current list).

## Format

A skill is a directory containing `SKILL.md` plus optional `references/`,
`scripts/`, `assets/`, and `examples/` subdirectories.

`SKILL.md` frontmatter (YAML, delimited by `---`):

| Field | Required | Notes |
|---|---|---|
| `name` | yes | `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤64 chars, must equal the directory name |
| `description` | yes | ≤1024 chars, states what the skill does and when to use it, no `<`/`>` |
| `license` | no | SPDX identifier |
| `allowed-tools` | no | tools pre-approved for this skill (client-interpreted) |
| `compatibility` | no | ≤500 chars, free text on environment needs |
| `metadata` | no | free-form nested map |

This repo's canonical `SKILL.md` files use only these six fields — no
vendor-specific frontmatter — so the same file works unmodified everywhere
a client reads plain Agent Skills.

## Discovery mechanism (progressive disclosure)

1. **Discovery**: client loads every skill's `name` + `description` at
   startup — cheap, so an agent can carry many skills.
2. **Activation**: when a task matches a description, the client loads the
   full `SKILL.md` body into context.
3. **Execution**: the agent follows the instructions, reading
   `references/`, running `scripts/`, or using `assets/` only as the
   instructions direct.

## Where clients look for skills

There's no single universal path — every client defines its own discovery
directory (see `clients/claude-code.md`, `clients/codex.md`,
`clients/github-copilot.md`). `scripts/install_skills.py` copies a skill
from this repo's `skills/` into whatever target directory you point it at,
rather than assuming one "correct" path.

## How to install these skills into an unlisted client

If your client supports the open spec but isn't documented in `clients/`
yet: find where it reads skills from (check its docs — do not guess), then:

```bash
python scripts/install_skills.py --skill <name> --target <that-directory>
```

## Verifying a skill is well-formed, independent of any client

```bash
python scripts/validate_skills.py
```

If the reference `skills-ref` CLI is installed
(`uv tool install git+https://github.com/agentskills/agentskills#subdirectory=skills-ref`),
`validate_skills.py` also runs `skills-ref validate` per skill automatically.
