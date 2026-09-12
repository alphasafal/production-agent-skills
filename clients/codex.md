# OpenAI Codex / ChatGPT

**Status**: 🟡 Expected/standard-compatible — based on Codex's published
documentation for the open Agent Skills format. Not independently tested in
a live Codex session for this repository.

Source: [learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills)
(the canonical `developers.openai.com/codex/skills` URL redirects here).

## Official skill support

Yes — Codex and ChatGPT support `SKILL.md` per the open spec.

## Expected skill format

Standard `SKILL.md` + `references/`/`scripts/`/`assets/`, per
`clients/generic-agent-skills.md`. Codex additionally supports an optional
`agents/openai.yaml` for UI metadata (display name, icon, brand color) and
invocation policy (e.g. `policy.allow_implicit_invocation: false`) — not
used by this repo's canonical skills, to keep one file working everywhere.

## Location / import mechanism

Codex scans, in priority order:

| Scope | Path |
|---|---|
| Repo (cwd) | `.agents/skills` |
| Repo (parent) | `../.agents/skills` |
| Repo (root) | `.agents/skills` at the repository root |
| User | `~/.agents/skills` |
| Admin | `/etc/codex/skills` |
| System | bundled with Codex |

Install with:

```bash
python scripts/install_skills.py --skill debugging-investigator --target ./.agents/skills
python scripts/install_skills.py --all --target ./.agents/skills
```

Note: Codex does not merge skills that share a `name` across scopes — both
appear in skill selectors, so avoid installing the same skill at two
overlapping scopes if that would be confusing.

## Verifying discovery

Not verified — check current Codex/ChatGPT documentation and UI for how
installed skills are surfaced (e.g. a skills list in settings, or the `$`/`@`
mention picker).

## Explicit invocation

- Codex CLI: `$skill-name`
- ChatGPT: `@skill-name`, or type `$` to bring up a picker

## Automatic activation

Implicit — Codex matches the task description against loaded skills'
`name`/`description`. Progressive disclosure here has a stated budget: the
initial skill list is capped at roughly 2% of the context window or 8,000
characters, with the full `SKILL.md` loaded only once a skill is selected.

## Tool/script limitations

Not verified — the specific sandboxing/permission model for scripts under
`scripts/` in a given Codex environment (CLI vs. IDE extension vs. cloud)
is not fully documented in the sources checked for this repo. Test in your
own environment before relying on the `data-scientist` skill's bundled
scripts running unattended.

## MCP/app considerations

`agents/openai.yaml` supports declaring an MCP tool dependency
(`dependencies.tools: [{type: mcp}]`) for skills that need one — none of
this repo's skills declare a hard MCP dependency; where an MCP-connected
tool would help (observability tooling for `debugging-investigator`,
research tools for `research-to-decision`), the SKILL.md says so as
optional, not required.

## Troubleshooting

- **Skill not found**: confirm it was installed to one of the scanned
  paths above, and that the directory name matches `name:` in the
  frontmatter.
- Everything else: **Not verified — check current Codex documentation.**
