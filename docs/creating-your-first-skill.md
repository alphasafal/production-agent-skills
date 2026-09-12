# Creating Your First Skill

## First: should this be a skill at all?

- [ ] Is this a task you (or your team) do **more than once**?
- [ ] Does doing it well require a **specific procedure**, not just
      general competence? (If any reasonable approach works fine, a skill
      adds ceremony without value.)
- [ ] Can you describe **when it should trigger** in a sentence or two,
      distinctly from neighboring tasks?
- [ ] Can you name a **concrete output** it should produce?

If you answered no to any of these, you probably want a one-off prompt
instead — see [skills-vs-prompts.md](skills-vs-prompts.md).

## Steps

### 1. Scaffold the directory

```
skills/my-skill/
└── SKILL.md
```

`my-skill` (the directory name) must exactly match the `name:` field
you'll put in the frontmatter.

### 2. Write the frontmatter

```yaml
---
name: my-skill
description: >
  <what it does>. Use when <trigger vocabulary a real request would
  contain>. Do not use for <explicit exclusions>.
license: MIT
---
```

Spend real effort on `description` — see
[skill-anatomy.md](skill-anatomy.md#the-description-field-is-the-most-important-line-in-the-file).
This is the field that determines whether your skill ever actually
activates.

### 3. Write the workflow as ordered steps

Pick the right degree of freedom for each step (see
[skill-anatomy.md](skill-anatomy.md#degrees-of-freedom)). Don't write "you
are an expert in X" — write the actual sequence of things to do.

### 4. Define the output contract

What file(s) or structured output does a correct run produce? If you can't
answer this, the workflow probably isn't concrete enough yet.

### 5. Move detail out of SKILL.md

If a section is getting long and only matters in some cases, it belongs in
`references/`, with a conditional pointer from `SKILL.md` — see
[progressive-disclosure.md](progressive-disclosure.md). Keep `SKILL.md`
itself under roughly 400 lines (`scripts/validate_skills.py` will flag it).

### 6. Add scripts for anything deterministic

If part of the workflow has one correct, reusable, mechanical answer
(compute a statistic, check a pattern, validate a format), write a script
in `scripts/` instead of describing the computation in prose. See
[skills/data-scientist/scripts/](../skills/data-scientist/scripts/) for
the pattern: standalone, `--help`-documented, stdlib-or-declared-deps only.

### 7. Write evaluation cases

At minimum, per `CONTRIBUTING.md`: 5 obvious positive triggers, 2 harder/
ambiguous positive triggers, 3 negative triggers (prompts that must NOT
activate it). Put them in `evaluations/activation/my-skill.json` following
`schemas/evaluation.schema.json` — copy the shape from any existing file
in that directory.

### 8. Write at least one worked example

`examples/` in your skill directory: a realistic prompt and what a correct
run's output looks like. This is both documentation and a de facto
regression check for future edits to the skill.

### 9. Validate

```bash
python scripts/validate_skills.py -v
pytest tests/
python scripts/inspect_skill.py my-skill
```

Fix everything `validate_skills.py` flags as an error before considering
the skill done; warnings are worth a look but aren't always actionable.

### 10. Try it for real

Install it into an actual client (`python scripts/install_skills.py
--skill my-skill --target <path>` — see `clients/` for target paths) and
run your positive-trigger prompts against it. A skill that's never
actually been exercised by an agent is unverified, no matter how clean it
looks on paper.
