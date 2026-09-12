# Example 1: Understand a Repository

**Skill**: [repo-architect](../../skills/repo-architect/)

## Try it

Point an agent with `repo-architect` installed at any unfamiliar repository
(your own, or any of the four kinds shown below) and ask:

> "I just cloned this repo and have no idea how it's structured. Can you map it out for me?"

## What a correct run produces

`ARCHITECTURE.md`, `MODULE_MAP.md`, `DEPENDENCY_MAP.md`, `RISK_REGISTER.md`
— built entirely from files actually read, with **no code modified** during
the investigation (the skill explicitly forbids this).

## Worked examples by stack

The skill's own `examples/` directory shows the expected output shape for
four different kinds of repos — read whichever matches what you're pointing
it at:

- [Next.js repository](../../skills/repo-architect/examples/nextjs-repository.md)
- [Python service](../../skills/repo-architect/examples/python-service.md)
- [Go backend](../../skills/repo-architect/examples/go-backend.md)
- [Monorepo](../../skills/repo-architect/examples/monorepo.md)

## Grading a real run

See [`evaluations/workflows/repo-architect.json`](../../evaluations/workflows/repo-architect.json)
for the specific behaviors a correct run should exhibit.
