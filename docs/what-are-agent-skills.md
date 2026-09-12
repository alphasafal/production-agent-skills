# What Are Agent Skills?

An **Agent Skill** is a folder of instructions (and optionally scripts,
reference docs, and templates) that teaches an AI agent how to perform a
specific, repeatable task consistently. It's a folder containing at minimum
one file, `SKILL.md`, with two required pieces of metadata — `name` and
`description` — and a Markdown body of instructions.

```
debugging-investigator/
├── SKILL.md            # required: metadata + instructions
├── references/         # optional: detailed docs loaded only when needed
├── scripts/             # optional: deterministic code the agent can run
├── assets/              # optional: templates/boilerplate to fill in
└── examples/            # optional: worked examples of the output
```

Skills are an **open format** — [agentskills.io](https://agentskills.io) —
originally developed by Anthropic and now supported by a wide range of
agent products (Claude Code, OpenAI Codex, GitHub Copilot, Cursor, and
others). A skill written once, following the open spec, works unmodified
across any compliant client.

## Why a skill instead of just... telling the agent what to do?

Because "telling the agent what to do" doesn't survive past one
conversation. A skill is:

- **Portable** — a folder you can commit to a repo, share with a team, or
  publish, and it works the same way for anyone who installs it.
- **Progressive** — the agent only loads the full instructions when the
  task actually needs them (see [progressive-disclosure.md](progressive-disclosure.md)),
  so you can have dozens of skills available without bloating every prompt.
- **Testable** — because a skill's behavior is a concrete file with a
  defined contract, you can write activation and workflow tests against it
  (see [evaluating-skills.md](evaluating-skills.md)) — you can't write a
  test against "I told it to be careful" in a one-off chat message.
- **Composable** — skills can be installed and used together, each owning
  a distinct stage of a larger workflow (see [composing-skills.md](composing-skills.md)).

## What a good skill actually encodes

Not "you are an expert in X" — that's a persona, not a procedure. A real
skill encodes:

```
TRIGGER → INPUTS → PROCEDURE → TOOLS/RESOURCES → OUTPUT CONTRACT
        → QUALITY CHECKS → FAILURE/EDGE CASE HANDLING
```

Every skill in this repository ([skills/](../skills/)) follows this shape.
See [skill-anatomy.md](skill-anatomy.md) for the concrete file structure
that implements it.

## Where to go next

- New to the concept? Read [skills-vs-prompts.md](skills-vs-prompts.md).
- Wondering how this relates to tools/MCP/subagents?
  Read [skills-vs-tools.md](skills-vs-tools.md),
  [skills-vs-mcp.md](skills-vs-mcp.md), [skills-vs-subagents.md](skills-vs-subagents.md).
- Ready to install one? See the root [README](../README.md#quick-start).
- Ready to build your own? See [creating-your-first-skill.md](creating-your-first-skill.md).
