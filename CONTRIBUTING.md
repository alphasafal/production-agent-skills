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
   contract`, `# Quality checks`, `# Red flags`, `# Common
   rationalizations`, `# Edge cases`, `# References`). The validator
   enforces all twelve, in order.
   - **Red flags** (≥3): observable signs the agent is skipping the
     workflow ("you are editing code and can't name the command that
     reproduces the failure").
   - **Common rationalizations** (≥3 table rows): the excuses an agent uses
     to skip steps, each with why it doesn't hold. Agents rarely fail by
     not knowing a procedure; they fail by talking themselves out of it.
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
6. **A workflow scenario** in `evaluations/workflows/<your-skill>.json`
   (schema: `schemas/workflow.schema.json`) with `workspace_files` the agent
   gets and, if you have one, a `reference_answer` only the grader sees.
   Pressure scenarios (`evaluations/workflows/pressure/`) are encouraged:
   a prompt that argues for skipping your workflow, to check it holds.
7. **Routing passes**: `python scripts/run_routing_evals.py` must stay
   green for the *whole catalog* — your description has to win its own
   prompts without stealing other skills'. For a negative case that belongs
   to another skill, set `route_to` so the gate checks it.

## PR checklist (mirrors `.github/PULL_REQUEST_TEMPLATE.md`)

- What workflow does this skill encode?
- Why should it be a reusable skill rather than a one-off prompt?
- What are its activation triggers?
- What should NOT activate it?
- How did you test it? (`python scripts/validate_skills.py -v`, `pytest
  tests/`, and ideally an actual run against a real agent — see
  `docs/creating-your-first-skill.md` step 10)

## Frontmatter gotcha: the spec uses a strict YAML subset

Write block-style lists, not flow style — the reference parser rejects
`[a, b]` even though it's valid YAML:

```yaml
metadata:
  composes_with:
    - repo-architect       # correct
# composes_with: [repo-architect]   <- rejected by the spec's parser
```

Anchors/aliases/tags and duplicate top-level keys are also rejected.
`scripts/validate_skills.py` enforces all of this locally so you'll catch
it before CI does. Full explanation:
`clients/generic-agent-skills.md#gotcha-frontmatter-uses-a-strict-yaml-subset`.

## Local validation before opening a PR

```bash
python scripts/validate_skills.py -v
python scripts/run_static_evals.py
python scripts/run_routing_evals.py
pytest tests/
```

All four should be clean (warnings are worth reading, but only errors
block CI — see `.github/workflows/validate-skills.yml`).

Optionally, check against the reference implementation exactly as CI does:

```bash
uvx --from "git+https://github.com/agentskills/agentskills#subdirectory=skills-ref" \
  skills-ref validate skills/your-skill
```

## Editing an existing skill

Keep the same structure and section order. If you're adding significant
new domain detail, put it in `references/` with a conditional pointer from
`SKILL.md` rather than growing `SKILL.md` itself — see
`docs/progressive-disclosure.md`. If your change affects how the skill
activates, update its `evaluations/activation/<skill>.json` cases too.

### Description changes and the held-out set

`evaluations/routing/holdout.json` holds prompts that were written *after*
the descriptions were last tuned. Never edit a description just to fix a
holdout miss — that turns the holdout into training data and the number
stops meaning anything. If a miss reveals a real gap, add a new case to
`evaluations/activation/` and fix against that. Description edits also
spend the discovery budget: CI fails if `skills-ref to-prompt` for all
skills exceeds 8,000 characters.

### Changing plugins, packs or commands

Slash commands live in `slash-commands/`. After editing `packs.json`, a
command, or a skill's name, run `python scripts/build_marketplace.py`. It
regenerates `.claude-plugin/marketplace.json` and `plugin-packs/`, and CI
fails if they're stale. Before a release, run
`python scripts/verify_plugin_install.py`. It installs every plugin with the
real Claude Code CLI and checks that each one loads with exactly the right
skills and commands. This catches load failures that
`claude plugin validate` misses.

### Measuring a change for real

```bash
python scripts/run_behavioral_evals.py --skill your-skill --runs 3
```

runs the workflow scenarios with and without the skill and grades both
blind. Put before/after numbers for behavior-changing edits in the PR.

## Reporting a skill that didn't work well

Open an issue describing the prompt, what the skill actually did, and what
you expected per its `SKILL.md`. This is exactly the kind of feedback that
should turn into a new eval case (positive, ambiguous, or negative) so the
gap gets caught mechanically next time.
