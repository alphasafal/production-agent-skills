## What workflow does this skill encode?

<!-- The repeated real-world task this turns into a procedure. -->

## Why should it be a reusable skill?

<!-- What makes this worth packaging rather than a one-off prompt? -->

## What are its activation triggers?

<!-- Point to the positive cases in evaluations/activation/<skill>.json -->

## What should NOT activate it?

<!-- Point to the negative cases. What neighboring task could be confused for this one? -->

## How did you test it?

- [ ] `python scripts/validate_skills.py -v` passes with no errors
- [ ] `pytest tests/` passes
- [ ] `python scripts/run_static_evals.py` passes
- [ ] `python scripts/run_routing_evals.py` passes (whole catalog, not just this skill)
- [ ] Ran `python scripts/run_behavioral_evals.py --skill <name> --runs 3` (paste the summary table below)

<!-- Paste the with/without-skill summary table, model and date. For edits to an
existing skill, include before and after. -->

## Checklist (see CONTRIBUTING.md)

- [ ] `SKILL.md` follows the standard section order, including `# Red flags` and `# Common rationalizations`
- [ ] A workflow scenario in `evaluations/workflows/` (and ideally a pressure scenario)
- [ ] At least 5 positive-obvious, 2 positive-ambiguous, 3 negative eval cases
- [ ] At least one worked example in `examples/`
- [ ] Output contract and quality checks are concrete, not generic
