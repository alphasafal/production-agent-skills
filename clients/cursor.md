# Cursor

**Status**: 🟡 Expected/standard-compatible — based on Cursor's published
documentation for Agent Skills. Not independently tested in a live Cursor
session for this repository.

Source: [cursor.com/docs/skills](https://cursor.com/docs/skills) (read
2026-11-12).

## Official skill support

Yes — Cursor loads `SKILL.md` skills per the open spec.

## Location / import mechanism

| Scope | Paths |
|---|---|
| Project | `.agents/skills/`, `.cursor/skills/` |
| User | `~/.agents/skills/`, `~/.cursor/skills/` |
| Compatibility (also loaded) | `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/` |

Cursor also discovers `.agents/skills/` and `.cursor/skills/` in nested
subdirectories; skills found there apply only to files inside that
subdirectory.

Because `.agents/skills/` is shared with Codex, Copilot and Gemini CLI, one
install serves all of them:

```bash
curl -fsSL https://raw.githubusercontent.com/alphasafal/production-agent-skills/main/install.sh | sh -s -- --pack frontend-engineer --agent cursor
# or, from a clone:
python scripts/install_skills.py --pack frontend-engineer --agent cursor
```

Add `--global` for `~/.agents/skills/`. If you already installed for Claude
Code into `.claude/skills/`, Cursor reads that directory too, so there is
nothing more to install.

## Explicit invocation

Type `/` in Agent chat and search for the skill's name. Per Cursor's
documentation a skill invoked this way applies to that one message.

## Automatic activation

Description-based, as in the open spec's activation stage.

## Tool/script limitations

Not verified — check current Cursor documentation for how `scripts/` files
are executed and approved before relying on the `data-scientist` skill's
bundled scripts running unattended.

## Troubleshooting

- **Skill not found**: confirm it is in one of the paths above and that the
  directory name matches `name:` in the frontmatter.
- **The same skill appears twice**: it is installed in more than one of the
  directories Cursor reads (for example both `.agents/skills/` and
  `.claude/skills/`). Remove one copy:
  `sh install.sh --skill <name> --agent cursor --uninstall`.
- Everything else: **Not verified — check current Cursor documentation.**
