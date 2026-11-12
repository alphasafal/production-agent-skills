# Compatibility Matrix

Legend: ✅ tested in this repo's build process · 🟡 expected/standard-compatible
per that client's published documentation, not independently tested ·
❌ unsupported · ❓ not yet tested / not verified in available documentation.

**Nothing here is marked ✅ without an actual check having been performed.**
See each `clients/*.md` file for exactly what was checked and how.

## Spec conformance (client-independent)

| Check | Status |
|---|---|
| All 15 skills pass the official `skills-ref validate` (reference implementation of the open spec) | ✅ verified — run per skill in CI |
| Frontmatter satisfies the spec's strict YAML subset (no flow collections, anchors, or duplicate keys) | ✅ verified — enforced by `scripts/validate_skills.py` and `tests/test_spec_strictness.py` |
| Discovery cost per role pack (`skills-ref to-prompt`) | ✅ measured — largest pack (tech-lead) **5,629 bytes**, every pack under Codex's documented 8,000-char skill-list ceiling; enforced per pack in CI. All 15 together: 13,826 bytes (fine for Claude Code; Codex users install by pack) |
| Tooling runs on the declared `requires-python = ">=3.9"` range | ✅ verified — full suite passes on 3.9, 3.11, and 3.13 (CI matrix) |
| Installed copies (not just source) remain spec-valid | ✅ verified — `skills-ref validate` run against skills installed into a real cloned repository |

## Per-client capability matrix

| | Claude Code | OpenAI Codex / ChatGPT | GitHub Copilot |
|---|---|---|---|
| Skill discovered from a documented path | ✅ (installed + directory structure confirmed) | 🟡 (per docs; `.agents/skills` et al.) | 🟡 (per docs; 4 documented paths) |
| Auto-activation on matching prompt | 🟡 (documented behavior; not re-verified live this pass) | 🟡 (documented behavior) | 🟡 (documented behavior) |
| Explicit invocation (`/name` or equivalent) | ✅ documented (`/skill-name`) | 🟡 documented (`$name` CLI / `@name` ChatGPT) | ❓ not verified |
| Scripts (`scripts/*.py`) executable by the agent | ✅ (this repo's `data-scientist` scripts run via a normal shell-tool call — no client-specific mechanism needed) | ❓ sandbox/permission model not verified | ❓ not verified |
| Filesystem access available | ✅ | 🟡 (assumed for a coding agent; not verified per-surface) | 🟡 (assumed for coding-focused surfaces; not verified for e.g. Copilot code review) |
| Network required | ❌ not required by any of the 15 skills (research-to-decision benefits from it if available) | ❌ not required | ❌ not required |
| MCP/app dependency | ❌ none hard-required (optional enrichment only, see `docs/skills-vs-mcp.md`) | ❌ none hard-required | ❌ none hard-required |
| Installer target path used | `.claude/skills/` or `~/.claude/skills/` | `.agents/skills/` (repo or user scope) | `.agents/skills/`, `.claude/skills/`, or `.github/skills/` |
| Tested status (overall) | ✅ install + structure | ❓ not tested | ❓ not tested |

## More clients, from their own documentation

| | Cursor | Gemini CLI | Claude desktop and web apps |
|---|---|---|---|
| Where skills are read from | `.agents/skills/`, `.cursor/skills/` (and `.claude/skills/`, `.codex/skills/` for compatibility); the same under `~` per user | `.agents/skills/`, `.gemini/skills/`; the same under `~` per user | Uploaded as a zip in Customize > Skills |
| What to run or download | `install.sh --agent cursor` | `install.sh --agent gemini` | `claude-app-<skill>.zip` from a release |
| Tested status | 🟡 per docs, not tested | 🟡 per docs, not tested | 🟡 archives checked against the documented upload rules on every build; upload itself not tested |

Sources and details: [`clients/cursor.md`](../clients/cursor.md),
[`clients/gemini-cli.md`](../clients/gemini-cli.md),
[`clients/claude-apps.md`](../clients/claude-apps.md).

## Installers

| Check | Status |
|---|---|
| `install.sh` installs, skips, updates and uninstalls correctly | ✅ verified — `tests/test_install_sh.py`, plus a CI job on Linux (GNU tools) and macOS (BSD tools) |
| `install.sh` works piped from stdin with a real download | ✅ verified — CI installs the commit under test that way on every push |
| `install.sh` and `install_skills.py` agree on every agent's directory | ✅ verified — parity test over each agent, project and `--global` |
| `install.sh` on Windows (Git Bash, WSL) | ❓ not tested — use `npx skills add` or `python scripts/install_skills.py` there |

## What "tested" actually means here

For Claude Code: `python scripts/install_skills.py` was run against real
target directories — including `.claude/skills/` inside a freshly cloned
copy of the Flask repository — and the resulting layout was confirmed
file-by-file against Claude Code's documented
`.claude/skills/<name>/SKILL.md` format. The installed copies were then
re-validated with the official `skills-ref` CLI to confirm installation
preserves spec validity, and the bundled `data-scientist` scripts were run
from their installed location against a real 891-row dataset. A live
session's auto-activation was not re-confirmed in this build pass (that
requires restarting a Claude Code session against the installed directory)
— see `clients/claude-code.md` for the exact caveat.

For Codex and Copilot: no live session was available to test against
during this build. Every row for those columns is sourced directly from
each vendor's own published documentation (cited in `clients/codex.md` and
`clients/github-copilot.md`) — not inferred, not guessed.

## Keeping this honest over time

If you personally verify a row (e.g. you confirm a skill actually
auto-activates in a live Codex session), update this table, the relevant
`clients/*.md` file, and cite what you did — a specific prompt, a specific
client version, a specific date — so the next reader can tell a real
test from a documentation summary.
