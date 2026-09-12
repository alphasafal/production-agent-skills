# Contributing

## Proposing a new skill

Before writing anything, check the criteria — a good skill is:

- A **repeated real-world task**, not a one-off.
- **Narrow and coherent** — one clear responsibility, not several tasks
  bundled together.
- **Useful to multiple people**, not specific to one person's private setup.
- Aimed at a **measurable improvement** over an agent working without it.
- **Not a giant prompt** — see `docs/skills-vs-prompts.md` and
  `docs/skill-anatomy.md` for what separates the two.

If your idea overlaps heavily with an existing skill (check `skills/`
first), consider whether it's actually a `references/` addition to that
skill instead of a new one.

## What a skill contribution must include

1. **`SKILL.md`** following the structure in `docs/skill-anatomy.md`
   (`# Purpose`, `# When to use`, `# When NOT to use`, `# Required
   inputs`, `# Workflow`, `# Tool & resource guidance`, `# Output
   contract`, `# Quality checks`, `# Edge cases`, `# References`).
2. **At least 5 positive (obvious-trigger) activation cases** and
   **at least 3 negative (must-not-trigger) activation cases** in
   `evaluations/activation/<your-skill>.json`, matching
   `schemas/evaluation.schema.json`. Two harder/ambiguous positive cases
   are strongly encouraged (see any existing skill's eval file for the
   pattern) — they're what actually tests whether activation depends on
   understanding intent rather than keyword matching.
3. **One realistic worked example** in `examples/` inside your skill
   directory, showing what a correct run's output looks like.
4. **A clear output contract** — what file(s)/structured output a correct
   run produces (see step 1).
5. **Quality checks** — a short checklist a reviewer (human or agent) can
   run against the output.

## PR checklist (mirrors `.github/PULL_REQUEST_TEMPLATE.md`)

- What workflow does this skill encode?
- Why should it be a reusable skill rather than a one-off prompt?
- What are its activation triggers?
- What should NOT activate it?
- How did you test it? (`python scripts/validate_skills.py -v`, `pytest
  tests/`, and ideally an actual run against a real agent — see
  `docs/creating-your-first-skill.md` step 10)

## Local validation before opening a PR

```bash
python scripts/validate_skills.py -v
python scripts/run_static_evals.py
pytest tests/
```

All three should be clean (warnings are worth reading, but only errors
block CI — see `.github/workflows/validate-skills.yml`).

## Editing an existing skill

Keep the same structure and section order. If you're adding significant
new domain detail, put it in `references/` with a conditional pointer from
`SKILL.md` rather than growing `SKILL.md` itself — see
`docs/progressive-disclosure.md`. If your change affects how the skill
activates, update its `evaluations/activation/<skill>.json` cases too.

## Reporting a skill that didn't work well

Open an issue describing the prompt, what the skill actually did, and what
you expected per its `SKILL.md`. This is exactly the kind of feedback that
should turn into a new eval case (positive, ambiguous, or negative) so the
gap gets caught mechanically next time.
