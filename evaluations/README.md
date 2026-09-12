# Evaluations

This directory proves — or lets you prove — that each skill actually changes
agent behavior for the better, rather than asserting it.

## Structure

```
evaluations/
├── activation/   10 cases per skill: should this skill trigger on this prompt?
├── workflows/    1 richer scenario per skill: does the FULL workflow hold up?
├── fixtures/     small input files the workflow scenarios grade against
└── results/      where real before/after numbers go once you run them
```

## activation/ — does the skill trigger correctly?

Each `activation/<skill>.json` has 10 cases in three categories:

- **positive-obvious** (5): a clear trigger — the skill should activate.
- **positive-ambiguous** (2): an indirect trigger with no obvious keyword
  match — tests whether activation depends on genuine understanding of
  intent, not string matching on the skill's own name.
- **negative** (3): a prompt that must NOT trigger the skill — usually a
  conceptual question, or a task that belongs to a neighboring skill.

Every case is validated against `schemas/evaluation.schema.json` by
`scripts/validate_skills.py` and `tests/test_eval_cases.py`.

`scripts/run_static_evals.py` runs a **static, lexical proxy** over these
cases — it checks structural completeness and flags cases with suspiciously
low/high vocabulary overlap for human review. **It does not call a model and
does not measure real activation accuracy.** Real activation accuracy
requires running these prompts through an actual agent with the skill
installed and recording whether it activated — see "Running a real
before/after comparison" below.

## workflows/ — does the full workflow hold up, not just activation?

Each `workflows/<skill>.json` is one deeper scenario: a realistic prompt,
optionally a fixture file to work from, the specific behaviors a correct
run must exhibit, behaviors that must NOT appear, and grading notes tying
it back to a worked example in the skill's own `examples/` directory. These
are meant for human (or LLM-judge) grading of a transcript, not automated
static checking — `tests/test_eval_cases.py` only checks the file is
well-formed.

## fixtures/

Small, self-contained inputs referenced by `workflows/*.json` — a synthetic
CSV with an injected leakage column, a diff with an injected concurrency
bug, etc. Kept intentionally tiny and synthetic: no real user data, no
external credentials, fully reproducible.

## Running the static checks

```bash
python scripts/validate_skills.py -v
python scripts/run_static_evals.py
pytest tests/test_eval_cases.py
```

## Running a real before/after comparison

This is the methodology for producing real numbers (see
`docs/evaluating-skills.md` for the full write-up):

1. Take a `workflows/<skill>.json` scenario (or an `activation/<skill>.json`
   prompt).
2. Run it through the target agent **without** the skill installed. Record
   the transcript.
3. Install the skill (`scripts/install_skills.py`) and run the identical
   prompt again. Record the transcript.
4. Grade both transcripts against `required_behaviors` /
   `forbidden_behaviors` / `expected_artifacts` — by a human reviewer or a
   separate LLM-judge pass, not by the same agent that produced the run.
5. Repeat across enough runs to say something about consistency, not just
   one lucky/unlucky sample — variance matters here as much as the mean.
6. Record results in `results/README.md` using the table there.

**No fabricated numbers exist anywhere in this repository.** Every metric
placeholder is marked `NOT YET BENCHMARKED` until someone actually runs this
process and records real results.
