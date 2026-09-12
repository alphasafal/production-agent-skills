# Anatomy of a Skill

```
skill-name/
├── SKILL.md          # required
├── references/       # optional — detail loaded on demand
├── scripts/           # optional — deterministic, runnable code
├── assets/            # optional — templates/boilerplate to fill in
└── examples/          # optional — worked examples of the output
```

## SKILL.md frontmatter

```yaml
---
name: debugging-investigator
description: >
  Investigates software failures using evidence-driven debugging: reproduction,
  hypothesis generation and ranking, targeted hypothesis testing, root-cause
  identification, minimal fixes, and regression verification. Use when
  diagnosing bugs, crashes, failing tests, unexpected behavior, production
  incidents, or performance regressions. Do not use for writing new features
  or answering conceptual questions with no actual failure to investigate.
license: MIT
compatibility: Needs shell/filesystem access to reproduce and run tests.
metadata:
  category: engineering
---
```

`name` must equal the directory name exactly, and `description` is the
single most important line in the file.

> **Write frontmatter in block style.** The spec's reference parser rejects
> flow-style collections (`composes_with: [a, b]`) even though PyYAML and
> your editor will accept them. Every skill in this repo hit this exact
> failure before it was caught — see
> [`clients/generic-agent-skills.md`](../clients/generic-agent-skills.md#gotcha-frontmatter-uses-a-strict-yaml-subset).

### The description field is the most important line in the file

It's the *only* thing loaded at discovery time (see
[progressive-disclosure.md](progressive-disclosure.md)), so it has to do
four jobs at once — this repo's `schemas/skill-manifest.schema.json` and
`scripts/validate_skills.py` check for the first two mechanically; the
last two need a human/agent read:

1. **What** the skill does, specifically — not "helps with code," but the
   actual named workflow ("evidence-driven debugging: reproduction,
   hypothesis generation...").
2. **When** to use it — trigger vocabulary a real request would contain
   ("bugs, crashes, failing tests, unexpected behavior, production
   incidents").
3. **When NOT to** — explicit exclusions prevent false-positive activation
   ("Do not use for writing new features or answering conceptual
   questions").
4. Kept under the spec's length limits (1024 chars) without losing 1-3.

Compare this to a bad description — `"Helps debug code."` — which fails
all four: no specifics, no trigger vocabulary, no exclusions, and it's so
short the agent has almost nothing to match against.

## SKILL.md body structure

Every skill in this repo follows the same section order (see any file
under [skills/](../skills/) for a full example):

```
# Purpose
# When to use
# When NOT to use
# Required inputs
# Workflow
# Tool & resource guidance
# Output contract
# Quality checks
# Edge cases
# References
```

- **Workflow** is the procedure itself — numbered, ordered steps, written
  at the right degree of freedom for each step (see below).
- **Tool & resource guidance** is where conditional pointers to
  `references/`/`scripts/` live (progressive disclosure, stage 3).
- **Output contract** defines exactly what the skill produces, so its
  output is checkable, not just "reasonable-sounding."
- **Quality checks** is a checklist the agent (or a reviewer) can run
  against the output before calling the task done.
- **Edge cases** names the specific situations that would otherwise cause
  the workflow to silently do the wrong thing.

## Degrees of freedom

Not every workflow step should be equally prescriptive:

- **High freedom** — judgment matters, multiple approaches are reasonable:
  *"Explore the repository and identify architectural boundaries."*
  ([repo-architect](../skills/repo-architect/SKILL.md))
- **Medium freedom** — a preferred pattern exists but needs adaptation:
  *"Evaluate candidate models against the selected baseline."*
  ([data-scientist](../skills/data-scientist/SKILL.md))
- **Low freedom** — correctness depends on deterministic behavior:
  *"Run `scripts/profile_dataset.py` against the supplied dataset."*
  ([data-scientist](../skills/data-scientist/SKILL.md))

Getting this wrong in either direction breaks the skill: over-scripting a
judgment call produces brittle, situation-blind instructions; leaving a
deterministic check as vague prose ("check for missing data") produces
inconsistent results across runs where a script would give an exact answer.
