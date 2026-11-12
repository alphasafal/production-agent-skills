# Client Compatibility

This directory documents how each specific agent client discovers and runs
skills from this repository. Start with
[`generic-agent-skills.md`](generic-agent-skills.md) for what's true
regardless of client; the other files cover client-specific paths,
invocation, and known limitations.

| Client | Doc | Status |
|---|---|---|
| Claude Code | [claude-code.md](claude-code.md) | ✅ install/structure tested, 🟡 live activation not independently confirmed |
| OpenAI Codex / ChatGPT | [codex.md](codex.md) | 🟡 expected/standard-compatible per docs, not tested |
| GitHub Copilot | [github-copilot.md](github-copilot.md) | 🟡 expected/standard-compatible per docs, not tested |
| Cursor | [cursor.md](cursor.md) | 🟡 expected/standard-compatible per docs, not tested |
| Gemini CLI | [gemini-cli.md](gemini-cli.md) | 🟡 expected/standard-compatible per docs, not tested |
| Claude desktop and web apps | [claude-apps.md](claude-apps.md) | 🟡 archives built to the documented upload rules, upload not tested |

See [`docs/compatibility.md`](../docs/compatibility.md) for the full
capability matrix (discovery, script execution, filesystem/network needs,
MCP dependency) across these clients.

## One directory for most of them

Codex, GitHub Copilot, Cursor and Gemini CLI each document `.agents/skills/`
(project) and `~/.agents/skills/` (user) as a place they read skills from.
Claude Code reads `.claude/skills/` and `~/.claude/skills/`. The installers
know both:

```bash
sh install.sh --pack sre --agent claude            # .claude/skills
sh install.sh --pack sre --agent codex             # .agents/skills; same for copilot, cursor, gemini
sh install.sh --pack sre --agent claude --global   # ~/.claude/skills
python scripts/install_skills.py --pack sre --agent claude   # same options, from a clone
```

`install.sh` also runs without a clone; see the README. For any client not
listed here, pass its skills directory with `--target`.

**We never invent an installation path.** Every path named in these docs
either comes from that vendor's current published documentation (cited
inline) or is explicitly marked `Not verified — check current client
documentation.`
