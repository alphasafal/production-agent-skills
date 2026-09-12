# Composing Skills

Skills are composable building blocks — a larger workflow can be built out
of several skills, each owning a distinct stage — but composition here
means **documented handoff**, not automatic mega-skill orchestration. No
skill in this repo silently invokes another; `feature-to-production` is
explicit that handoffs are one-directional and that a called skill must
not invoke it back (see its `SKILL.md`), which is what keeps the pipelines
below legible instead of turning into an opaque recursive chain.

## Pipeline A — build a software feature

```
research-to-decision → repo-architect → feature-to-production
                                              ↓
                                    production-code-review
                                              ↓
                                    debugging-investigator (only if
                                                             tests fail
                                                             unexpectedly)
```

- `research-to-decision` — if there's a real technology/approach choice to
  make first (e.g. "which queue should this use").
- `repo-architect` — understand the relevant part of the codebase before
  designing the change, if unfamiliar.
- `feature-to-production` — owns requirement → implementation →
  deployment/rollback planning; internally hands off to the next two.
- `production-code-review` — reviews the resulting diff.
- `debugging-investigator` — only invoked if verification turns up an
  unexpected failure with an unclear cause; not part of the happy path.

## Pipeline B — data-driven product decision

```
product-manager → data-scientist → research-to-decision
```

- `product-manager` — scopes the ambiguous idea into a specific, testable
  hypothesis and MVP.
- `data-scientist` — if the hypothesis needs existing data to evaluate
  (e.g. "would this actually move the metric we think it would").
- `research-to-decision` — if there's still a build-vs-buy or
  technology-choice dimension once the product shape is clear.

## Pipeline C — architecture change

```
repo-architect → system-design-reviewer → feature-to-production → production-code-review
```

- `repo-architect` — map the current system before proposing a change to it.
- `system-design-reviewer` — stress-test the proposed new architecture
  before any code is written.
- `feature-to-production` — implement it (internally invoking
  `production-code-review` itself, as in Pipeline A — shown separately
  here to make clear the review still happens).

## Why not a single "do everything" skill

A mega-skill that auto-loads every stage regardless of what's actually
needed defeats progressive disclosure (see
[progressive-disclosure.md](progressive-disclosure.md)) and makes it much
harder to tell, from reading `SKILL.md`, what will actually happen for a
given task. Each skill here has a narrow, coherent responsibility; a
pipeline is just a documented sequence of skills invoked because their
expertise is actually needed for the task at hand — never invoked
preemptively "just in case."

## Composing skills you write yourself

If you're building a new skill that naturally follows or precedes one of
these eight, say so explicitly in its `metadata.composes_with` frontmatter
field and in a `# References` note pointing to the related skill — see any
existing skill's frontmatter for the pattern — rather than duplicating that
skill's logic inline.
