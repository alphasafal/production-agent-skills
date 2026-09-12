# Compatibility Matrix

Legend: ✅ tested in this repo's build process · 🟡 expected/standard-compatible
per that client's published documentation, not independently tested ·
❌ unsupported · ❓ not yet tested / not verified in available documentation.

**Nothing here is marked ✅ without an actual check having been performed.**
See each `clients/*.md` file for exactly what was checked and how.

| | Claude Code | OpenAI Codex / ChatGPT | GitHub Copilot |
|---|---|---|---|
| Skill discovered from a documented path | ✅ (installed + directory structure confirmed) | 🟡 (per docs; `.agents/skills` et al.) | 🟡 (per docs; 4 documented paths) |
| Auto-activation on matching prompt | 🟡 (documented behavior; not re-verified live this pass) | 🟡 (documented behavior) | 🟡 (documented behavior) |
| Explicit invocation (`/name` or equivalent) | ✅ documented (`/skill-name`) | 🟡 documented (`$name` CLI / `@name` ChatGPT) | ❓ not verified |
| Scripts (`scripts/*.py`) executable by the agent | ✅ (this repo's `data-scientist` scripts run via a normal shell-tool call — no client-specific mechanism needed) | ❓ sandbox/permission model not verified | ❓ not verified |
| Filesystem access available | ✅ | 🟡 (assumed for a coding agent; not verified per-surface) | 🟡 (assumed for coding-focused surfaces; not verified for e.g. Copilot code review) |
| Network required | ❌ not required by any of the 8 skills (research-to-decision benefits from it if available) | ❌ not required | ❌ not required |
| MCP/app dependency | ❌ none hard-required (optional enrichment only, see `docs/skills-vs-mcp.md`) | ❌ none hard-required | ❌ none hard-required |
| Installer target path used | `.claude/skills/` or `~/.claude/skills/` | `.agents/skills/` (repo or user scope) | `.agents/skills/`, `.claude/skills/`, or `.github/skills/` |
| Tested status (overall) | ✅ install + structure | ❓ not tested | ❓ not tested |

## What "tested" actually means here

For Claude Code: `python scripts/install_skills.py` was run against a real
target directory, and the resulting layout was confirmed file-by-file
against Claude Code's documented `.claude/skills/<name>/SKILL.md` format.
A live session's auto-activation was not re-confirmed in this build pass
(that requires restarting a Claude Code session against the installed
directory) — see `clients/claude-code.md` for the exact caveat.

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
