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

See [`docs/compatibility.md`](../docs/compatibility.md) for the full
capability matrix (discovery, script execution, filesystem/network needs,
MCP dependency) across these clients.

**We never invent an installation path.** Every path named in these docs
either comes from that vendor's current published documentation (cited
inline) or is explicitly marked `Not verified — check current client
documentation.`
