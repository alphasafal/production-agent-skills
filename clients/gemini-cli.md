# Gemini CLI

**Status**: 🟡 Expected/standard-compatible — based on Gemini CLI's
published documentation for Agent Skills. Not independently tested in a
live Gemini CLI session for this repository.

Source: [geminicli.com/docs/cli/skills](https://geminicli.com/docs/cli/skills/)
(read 2026-11-12).

## Official skill support

Yes — Gemini CLI discovers `SKILL.md` skills per the open spec.

## Location / import mechanism

Lowest to highest precedence:

| Tier | Paths |
|---|---|
| Built-in | bundled with Gemini CLI |
| Extension | bundled with installed extensions |
| User | `~/.gemini/skills/`, `~/.agents/skills/` (alias) |
| Workspace | `.gemini/skills/`, `.agents/skills/` (alias) |

When two skills share a name the higher tier wins, and within a tier
`.agents/skills/` takes precedence over `.gemini/skills/`.

```bash
curl -fsSL https://raw.githubusercontent.com/alphasafal/production-agent-skills/main/install.sh | sh -s -- --pack backend-engineer --agent gemini
# or, from a clone:
python scripts/install_skills.py --pack backend-engineer --agent gemini
```

Both write to `.agents/skills/` (add `--global` for `~/.agents/skills/`),
which Codex, Copilot and Cursor read as well.

## Verifying discovery

```bash
gemini skills list --all    # from the terminal
/skills list                # inside a session
```

## Automatic activation

Description-based, as in the open spec's activation stage.

## Tool/script limitations

Not verified — check current Gemini CLI documentation for its sandbox and
approval model before relying on the `data-scientist` skill's bundled
scripts running unattended.

## Troubleshooting

- **Skill not listed**: confirm it is in one of the paths above and that the
  directory name matches `name:` in the frontmatter.
- Everything else: **Not verified — check current Gemini CLI documentation.**
