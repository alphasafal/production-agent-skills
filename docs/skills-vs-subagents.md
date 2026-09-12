# Skills vs. Subagents

A **subagent** is an isolated worker — a separate context/session spun up
to do a bounded piece of work and report back, so the main conversation's
context isn't spent on the details of how that piece got done.

A **skill** is a procedure any agent (main session or subagent) can load
and follow. Skills and subagents operate on different axes: a subagent is
about *where the work happens* (isolated context); a skill is about *how
the work is done* (the procedure), regardless of where it runs.

## They compose, not compete

A subagent tasked with "review this diff" benefits exactly as much from
`production-code-review`'s structured workflow and severity rubric as the
main agent would. The skill doesn't care whether it's loaded by the main
session or by a subagent — it's the same file either way.

Some clients (see `clients/claude-code.md`) even let a skill declare it
should run in an isolated subagent context (`context: fork` in Claude
Code's frontmatter extensions) — but that's a client-specific execution
detail layered on top of the skill, not something this repo's canonical,
portable `SKILL.md` files depend on, since not every client supports it.

## Rule of thumb

- Need to **isolate** a large or noisy piece of work from the main
  conversation's context? That's a subagent decision.
- Need the work, wherever it runs, to **follow a specific, repeatable
  procedure**? That's a skill.
- Often both: dispatch a subagent for `repo-architect`'s investigation (so
  the main conversation isn't flooded with every file read), and have that
  subagent load and follow the `repo-architect` skill to do it well.

## Avoid this anti-pattern

Don't build a "mega-skill" that itself spawns a chain of subagents running
other skills automatically. This repo's `feature-to-production` skill
deliberately does the opposite: it documents which skill *owns* each stage
(`repo-architect` for investigation, `production-code-review` for review,
`debugging-investigator` if tests unexpectedly fail) and hands off
one-directionally — see [composing-skills.md](composing-skills.md) — rather
than orchestrating them itself. Composition should stay legible: a human
reading the SKILL.md should be able to tell exactly what happens and when.
