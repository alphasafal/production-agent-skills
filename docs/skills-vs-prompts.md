# Skills vs. Prompts

A **prompt** is what you want right now, for this conversation. It's
ephemeral — write it, use it, it's gone (or buried in chat history where
nobody will find it again).

A **skill** is how the work should repeatedly be done, packaged so it
survives past this one conversation and works for anyone who installs it.

## Concretely, what's different

| | Prompt | Skill |
|---|---|---|
| Lifetime | This conversation | Committed to a repo, reused indefinitely |
| Discoverable by others | No | Yes — `name`/`description` show up in the agent's skill list |
| Testable | Not really | Yes — activation cases, workflow cases (see `evaluations/`) |
| Structure | Free-form text | A defined contract: trigger, inputs, procedure, output, quality checks |
| Detail management | Everything crammed into one message | Progressive disclosure — detail lives in `references/`, loaded only when needed |
| Improvable over time | Rewrite from scratch each time | Edit the file; the improvement applies to every future use |

## An example

**As a prompt** (works once, for this exact conversation):

> "Can you look into why our API sometimes returns 500s? Check the logs,
> try to reproduce it, and don't just guess at a fix — actually confirm
> what's causing it before changing anything."

That's a perfectly reasonable thing to type. But it only helps *this*
conversation. The next time someone on the team hits a similar bug, they
either remember to type something similarly careful, or they don't, and
the agent (or the person) jumps straight to a speculative fix.

**As a skill** ([skills/debugging-investigator/](../skills/debugging-investigator/)):
the exact same discipline — observe, reproduce, collect evidence, form and
rank hypotheses, confirm root cause before fixing — is captured once, as a
file, with an explicit rule ("never make a speculative change"), a defined
output (`DEBUG_REPORT.md`), and reference material for different failure
domains (web, database, network, concurrency, distributed systems,
performance). Anyone who installs the skill gets that discipline
automatically, every time, without having to type it out.

## When a prompt is actually the right tool

Not everything needs to be a skill. A one-off question, a task you'll
genuinely only do once, or something too idiosyncratic to generalize — just
ask directly. Turning every prompt into a skill is its own anti-pattern
(see [creating-your-first-skill.md](creating-your-first-skill.md) for the
"is this actually worth a skill" checklist).
