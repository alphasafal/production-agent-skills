# Evaluations

This directory proves — or lets you prove — that each skill actually changes
agent behavior for the better, rather than asserting it.

## Structure

```
evaluations/
├── activation/        10 cases per skill: should this skill trigger on this prompt?
├── routing/
│   └── holdout.json   prompts never used to tune descriptions (honest generalization check)
├── workflows/         1 end-to-end scenario per skill: does the FULL workflow hold up?
│   └── pressure/      scenarios where the prompt argues for skipping the workflow
├── fixtures/          small, synthetic inputs the scenarios run against
└── results/           published numbers (README.md) + raw runs (runs/, gitignored)
```

## The four tiers

| Tier | Question | Script | Model calls | In CI |
|---|---|---|---|---|
| 1. Structure | Is every skill and case well-formed, spec-valid, within budget? | `validate_skills.py`, `pytest` | none | ✅ gated |
| 2. Routing | Does the *catalog* send each prompt to the right skill? | `run_routing_evals.py` | none | ✅ gated |
| 3. Activation | Does a real agent actually load the right skill? | `run_behavioral_evals.py --mode activation` | yes | on demand |
| 4. Behavior | With the skill loaded, does the agent do the work better than without it? | `run_behavioral_evals.py` | yes | on demand |

Tiers 1–2 are free and deterministic, so they gate every PR. Tiers 3–4 cost
tokens and are run on demand, with results published in
[`results/README.md`](results/README.md).

## activation/ — does the skill trigger correctly?

Each `activation/<skill>.json` has 10 cases in three categories:

- **positive-obvious** (5): a clear trigger — the skill should activate.
- **positive-ambiguous** (2): an indirect trigger with no obvious keyword
  match — tests understanding of intent, not string matching.
- **negative** (3): must NOT trigger the skill. If the prompt belongs to a
  neighboring skill, `route_to` names it.

## Tier 2: routing (`scripts/run_routing_evals.py`)

An agent picks skills from their names and descriptions alone, so a skill
is only as good as its description is *distinct from the others*. This
script ranks all skills against every activation prompt (BM25 over the
name and the positive part of the description — "Do not use…" clauses are
excluded, since a word-counter would read them as evidence *for* the skill)
and gates:

- every obvious positive ranks its skill **#1 of all skills**
- every ambiguous positive ranks its skill in the **top 3**
- every negative with `route_to` ranks that other skill **above** this one
- no two descriptions are near-duplicates (TF-IDF cosine ≤ 0.45)
- ≥ 90% of `routing/holdout.json` prompts rank their skill in the top 3

It also reports — without gating — negatives like "What is Kafka?", which
a lexical scorer can't distinguish from "choose Kafka for us"; that's what
tier 3 is for.

**The held-out set** was written after the descriptions were last tuned
and is never used to tune them. If a holdout prompt misses, add a new
activation case and fix against *that*; editing a description to fix a
holdout miss makes the number meaningless.

## Tiers 3–4: behavioral (`scripts/run_behavioral_evals.py`)

Drives the real Claude Code CLI headlessly.

**Workflow mode** (default) runs every `workflows/**/*.json` scenario in
two arms — **baseline** (no skill) and **with_skill** — each in a
throwaway git workspace outside this repo containing only that scenario's
`workspace_files`. A separate grader call, which is *not told which arm it
is reading*, checks the transcript and workspace diff against
`required_behaviors`, `forbidden_behaviors` and `expected_artifacts`. If a
scenario has a `reference_answer`, only the grader sees it.

**Activation mode** installs all skills into one workspace, sends each
`activation/` prompt, and records which skill the agent actually loaded.

```bash
python scripts/run_behavioral_evals.py --dry-run                       # plan only, free
python scripts/run_behavioral_evals.py --skill debugging-investigator --runs 3
python scripts/run_behavioral_evals.py --kind pressure --runs 3
python scripts/run_behavioral_evals.py --mode activation
```

Raw transcripts, workspace diffs and gradings land in `results/runs/`
(gitignored). Publish the summary table in `results/README.md` with the
date, model and number of runs.

### Pressure scenarios

`workflows/pressure/` holds scenarios whose prompt pushes against the
skill: production is on fire, the CTO already approved it, we've sunk two
weeks into this, skip the tests. A skill that only works on polite prompts
isn't production-grade. These test the `# Red flags` and
`# Common rationalizations` sections of each SKILL.md directly.

## fixtures/

Small, self-contained, synthetic inputs: a churn CSV with an injected
leakage column and structured missingness, a payments diff with a
check-then-act race, and a tiny stdlib API (`public-api/`) to add rate
limiting to. No real user data, no credentials, fully reproducible.

## Running everything that's free

```bash
python scripts/validate_skills.py -v
python scripts/run_static_evals.py
python scripts/run_routing_evals.py
pytest tests/
```

**No fabricated numbers exist anywhere in this repository.** Every number
in `results/README.md` comes from a recorded run, labelled with its date,
model and run count.
