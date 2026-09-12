# Progressive Disclosure

Progressive disclosure is the mechanism that lets an agent carry many
skills without every skill's full content bloating every prompt. It works
in three stages, per the [open spec](https://agentskills.io):

```
DISCOVERY            ACTIVATION              EXECUTION
name + description → full SKILL.md body  →  references/scripts/assets
(always loaded,       (loaded only when       (loaded only when the
 cheap)                the task matches)       instructions say to)
```

## Stage 1: Discovery

At startup, the agent loads only `name` and `description` for every
available skill. This is why description quality matters so much — see
[skill-anatomy.md](skill-anatomy.md#the-description-field-is-the-most-important-line-in-the-file).
A vague description means the agent can't decide when to activate the
skill without reading the whole thing, defeating the point.

## Stage 2: Activation

When a task matches a skill's description, the full `SKILL.md` body loads.
This is why `SKILL.md` itself should stay lean — this repo enforces a
soft ceiling (`scripts/validate_skills.py` flags anything over 400 lines)
specifically so activation stays cheap even for a skill the agent ends up
not using much of.

## Stage 3: Execution — the part people get wrong

This is where most of the actual domain knowledge should live, loaded
**only when the instructions say to**, not dumped into `SKILL.md` "just in
case." Two ways this repo's skills do it:

**Conditional references** — `SKILL.md` names the exact condition under
which a reference file matters:

> "If the failure involves timeouts, retries, or cross-service calls, read
> `references/network-debugging.md`."
> — [skills/debugging-investigator/SKILL.md](../skills/debugging-investigator/SKILL.md)

This is deliberately specific. Compare to the anti-pattern:

> "See references for more information."

The first tells the agent exactly when to spend the context budget; the
second forces it to guess or read everything, which is what progressive
disclosure exists to avoid.

**Deterministic scripts, not narrated procedures** — where the correct
behavior is exact and reusable (compute missingness, check for leakage
patterns), it's a script in `scripts/` that gets *run*, not a page of
prose the agent re-derives by reasoning every time. See
[skills/data-scientist/scripts/](../skills/data-scientist/scripts/).

## Avoid deeply nested reference chains

A reference file that itself points to three more reference files, each
pointing further, defeats progressive disclosure by turning "load this one
thing when needed" into a treasure hunt. Every skill in this repo keeps
references one level deep from `SKILL.md` — check any skill's
`references/` directory for the pattern.

## The practical test

Ask: "if the agent never reads this reference file, does `SKILL.md` still
work?" If a reference is load-bearing for `SKILL.md`'s own instructions to
make sense, it's not actually optional — either fold it into `SKILL.md` or
make the pointer to it unconditional rather than an "if needed" note.
