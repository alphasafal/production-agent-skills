# Claude Code

**Status**: ✅ Tested (install + structure), 🟡 not independently confirmed
(live in-session auto-activation). What was actually verified while
building this repo: `scripts/install_skills.py` was run against a real
`.claude/skills/` target directory, and the resulting file layout was
confirmed to match this doc's table exactly (correct nesting, no stray
files, `SKILL.md` present per skill). What was **not** re-verified in this
build pass: starting a fresh Claude Code session against the installed
directory and confirming `/debugging-investigator` actually appears in the
menu and auto-activates on a matching prompt — that requires a session
restart this build process didn't perform. If you install a skill and it
doesn't show up, see Troubleshooting below before filing an issue.

Source: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills).

## Official skill support

Yes — native support for the open Agent Skills format.

## Expected skill format

Standard `SKILL.md` + `references/`/`scripts/`/`assets/`/`examples/`, per
`clients/generic-agent-skills.md`. Claude Code additionally understands
(all optional, none used in this repo's canonical skills, since they're
Claude-specific and would reduce portability):

- `disable-model-invocation: true` — skill only runs via explicit `/name`.
- `user-invocable: false` — hide from the `/` menu; agent-only.
- `allowed-tools` — pre-approve tools for the skill's turn.
- `context: fork` — run the skill in an isolated subagent context.

## Location / import mechanism

| Location | Path | Scope |
|---|---|---|
| Project | `.claude/skills/<name>/SKILL.md` | This repo, committed, shared with the team |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects on this machine |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` | Sessions in/below that subdirectory |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled |

Install with:

```bash
python scripts/install_skills.py --skill debugging-investigator --target ./.claude/skills
# or, for every skill:
python scripts/install_skills.py --all --target ./.claude/skills
```

For personal (cross-project) install, target `~/.claude/skills` instead.

## Verifying discovery

Start (or restart) a Claude Code session in the project and type `/` — the
installed skill should appear in the menu by its directory name (e.g.
`/debugging-investigator`). Claude Code also picks up live edits to
already-loaded project skills without a restart.

## Explicit invocation

```
/debugging-investigator
/debugging-investigator "the argument text, if the skill declares an arguments field"
```

Skills can be stacked: `/write-tests /fix-issue 123`.

## Automatic activation

Claude Code matches the current task against each loaded skill's
`description` and reads the full `SKILL.md` in when it matches — this is
why `description` quality matters so much (see `docs/skill-anatomy.md`).

## Tool/script limitations

- None of this repo's skills use Claude Code's `!`-prefixed inline shell
  execution (kept out for portability — see Phase-level design note in
  `docs/architecture.md`). The `data-scientist` skill's scripts are run by
  the agent explicitly via a normal shell tool call, which works
  identically everywhere.
- **Personal skills** (`~/.claude/skills/`) don't load in Cowork or cloud
  sessions — install at the project level for those.
- Script execution via `!` commands can be globally disabled
  (`disableSkillShellExecution`) — not relevant here since this repo
  doesn't rely on that mechanism.

## MCP/app considerations

None of these skills require an MCP server to function; `debugging-investigator`
and `system-design-reviewer` note that a connected observability/tracing
MCP server (if available) improves distributed-systems investigations, but
it's optional, not required.

## Troubleshooting

- **Skill doesn't show up in `/`**: confirm the directory name matches
  `name:` in its frontmatter exactly, and that `SKILL.md` starts with `---`
  on the very first line.
- **Skill shows up but doesn't auto-activate**: the `description` may not
  match your phrasing closely enough — try invoking it explicitly with
  `/skill-name` instead, or check `evaluations/activation/<skill>.json`
  for the phrasing this skill was designed to trigger on.
- **Not verified**: behavior with `skillOverrides` or enterprise-managed
  skill directories — check current Claude Code documentation.
