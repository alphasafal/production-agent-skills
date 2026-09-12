# GitHub Copilot

**Status**: 🟡 Expected/standard-compatible — based on GitHub's published
documentation for Agent Skills. Not independently tested in a live Copilot
session for this repository.

Source: [docs.github.com/en/copilot/concepts/agents/about-agent-skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).

## Official skill support

Yes. Per GitHub's documentation: "Agent skills work with Copilot cloud
agent, Copilot code review, the GitHub Copilot CLI, the GitHub Copilot
app, and agent mode in Visual Studio Code and JetBrains IDEs."

## Expected skill format

Standard `SKILL.md` + `references/`/`scripts/`/`assets/`, per
`clients/generic-agent-skills.md`. GitHub's documentation does not specify
Copilot-only frontmatter extensions in the sources checked — this repo's
canonical skills use only the open-spec fields, which should be maximally
compatible regardless.

## Location / import mechanism

| Scope | Paths |
|---|---|
| Project | `.github/skills`, `.claude/skills`, or `.agents/skills` |
| Personal | `~/.copilot/skills` or `~/.agents/skills` |

Because `.agents/skills` and `.claude/skills` are both recognized, a single
install can serve Copilot alongside Codex or Claude Code without
duplication:

```bash
python scripts/install_skills.py --all --target ./.agents/skills
```

GitHub CLI can also discover/install skills directly from a repository via
`gh skill` (see the GitHub Changelog announcement for `gh` skill
management) — **not verified** whether it can install skills from an
arbitrary path like this repo's `skills/` directory versus a
purpose-built skill package; check current `gh skill --help` output.

## Verifying discovery

Not verified — check the Copilot surface you're using (VS Code agent mode,
CLI, coding agent) for however it lists currently-loaded skills.

## Explicit invocation

Not verified — check current documentation for whether Copilot supports an
explicit `/skill-name`-style invocation or relies on automatic matching only.

## Automatic activation

Per GitHub's documentation, skills "load when relevant to improve
[Copilot's] performance in specialized tasks" — implies automatic,
description-based matching similar to the open spec's activation stage.

## Tool/script limitations

Not verified — GitHub's documentation confirms skills are "folders of
instructions, scripts, and resources that Copilot can load," but does not
detail the execution sandbox/permission model for `scripts/` across each
Copilot surface (cloud agent vs. local CLI vs. IDE agent mode likely
differ). Test in your specific environment before depending on
`data-scientist`'s bundled scripts running unattended.

## MCP/app considerations

Not verified — check current documentation for how Copilot surfaces handle
a skill that expects an optional MCP-connected tool (none of this repo's
skills require one).

## Troubleshooting

- **Skill not found**: confirm it's in one of the four documented paths
  above and the directory name matches `name:` in the frontmatter.
- Everything else: **Not verified — check current GitHub Copilot
  documentation** for the specific surface (VS Code, CLI, cloud agent,
  code review) you're using, since behavior may differ across them.
