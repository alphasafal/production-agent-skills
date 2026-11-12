# Claude desktop and web apps

**Status**: 🟡 Built to Anthropic's documented packaging rules, checked on
every build. **Not yet tested by uploading to the app** — if an upload is
rejected, please [open an issue](https://github.com/alphasafal/production-agent-skills/issues)
with the message the app shows.

Sources: Anthropic help center,
[Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
and [How to create custom skills](https://support.claude.com/en/articles/12512198)
(read 2026-11-12).

## What to download

Each [release](https://github.com/alphasafal/production-agent-skills/releases/latest)
has one `claude-app-<skill>.zip` per skill, for example
`claude-app-product-manager.zip`. The app takes one skill per upload.

## Uploading

Per the help article:

1. Skills need code execution: in **Settings > Capabilities**, turn on
   code execution and file creation. Without it skills appear greyed out.
2. Open **Customize > Skills**.
3. Click **+**, then **Create skill**, then **Upload a skill**.
4. Choose the zip. The skill appears in your list with an on/off toggle.

On Team and Enterprise plans an owner can restrict who may upload skills;
see the help article for the organization settings.

## How these zips differ from the repository

One line. The help article gives a 200-character limit for a skill's
`description`; the descriptions in this repository are 650–870 characters,
because coding agents use that room to decide when to load a skill (the
open spec allows 1,024). Each `claude-app-*.zip` therefore carries the
skill's `metadata.short_description` as its description. The workflow,
references, scripts and examples are byte-for-byte the same.

What the build checks for every archive (`scripts/package_skills.py`,
`tests/test_packaging.py`):

| Rule from the help article | Checked |
|---|---|
| The zip contains the skill folder at its root, not loose files | ✅ |
| The folder name equals the skill's `name` | ✅ |
| `SKILL.md` is present and starts with YAML frontmatter | ✅ |
| `name` is at most 64 characters | ✅ |
| `description` is at most 200 characters | ✅ |

## Which skills make sense in a chat app

All 15 upload the same way, but several expect a repository and a shell
(`repo-architect`, `debugging-investigator`, `test-first-developer`,
`feature-to-production`). The ones that work from a pasted document or an
attached file are the natural fit: `product-manager`, `research-to-decision`,
`spec-and-plan`, `system-design-reviewer`, `threat-modeler`,
`incident-responder` (postmortems and status updates), and `data-scientist`
with an uploaded CSV. The benchmark numbers in this repository were
measured in Claude Code with the full descriptions, not in the apps.

## Building the zips yourself

```bash
python scripts/package_skills.py     # writes dist/, including SHA256SUMS
```
