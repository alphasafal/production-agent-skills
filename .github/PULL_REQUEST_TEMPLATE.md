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
- [ ] Ran the skill against a real agent at least once (describe below)

<!-- Describe the real run, if any: what prompt, what client, what happened. -->

## Checklist (see CONTRIBUTING.md)

- [ ] `SKILL.md` follows the standard section order
- [ ] At least 5 positive-obvious, 2 positive-ambiguous, 3 negative eval cases
- [ ] At least one worked example in `examples/`
- [ ] Output contract and quality checks are concrete, not generic
