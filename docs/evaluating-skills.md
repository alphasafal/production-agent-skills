# Evaluating Skills

A skill you can't measure is a claim, not an engineering artifact. This
repo separates two questions, because they need different evidence:

1. **Does it activate correctly?** (`evaluations/activation/`)
2. **Does the full workflow actually hold up when it activates?**
   (`evaluations/workflows/`)

See [evaluations/README.md](../evaluations/README.md) for the directory
structure and how to run the static checks. This doc covers the
methodology for a *real* before/after measurement.

## Metrics worth measuring

- **Activation accuracy** — of the 10 cases per skill (5 obvious positive,
  2 ambiguous positive, 3 negative), how many activate/don't-activate
  correctly?
- **Workflow completion** — of the `required_behaviors` in a
  `workflows/<skill>.json` scenario, how many were actually observed?
- **Forbidden-behavior rate** — did any `forbidden_behaviors` show up
  anyway (e.g. a speculative fix before evidence, for
  `debugging-investigator`)?
- **Output-schema adherence** — were the `expected_artifacts` actually
  produced, in the specified shape?
- **Tool-use success** — for skills with bundled scripts
  (`data-scientist`), were they actually invoked, and did they run cleanly?
- **Reference-use correctness** — did the agent read the conditionally-
  pointed-to reference file when the condition applied (e.g.
  `references/time-series.md` for a time-series dataset)?
- **Hallucination rate** — specific to `research-to-decision`: any
  uncited factual claim presented as fact rather than flagged as an
  assumption.
- **Human-review score** — a 1-5 (or pass/fail) judgment from a human (or
  a separate LLM-judge pass) reading the transcript against the scenario's
  `grading_notes`.

## Methodology: WITHOUT skill vs. WITH skill

1. Pick a scenario — an `activation/<skill>.json` prompt for a quick check,
   or a `workflows/<skill>.json` scenario for a full workflow measurement.
2. **Baseline run**: give the agent the same prompt with the skill **not**
   installed. Record the full transcript.
3. **Skill run**: install the skill
   (`python scripts/install_skills.py --skill <name> --target <path>`),
   give the identical prompt, record the transcript.
4. **Grade both** transcripts against the scenario's `required_behaviors`
   / `forbidden_behaviors` / `expected_artifacts` — ideally by a reviewer
   (human or a separate LLM-judge call) who didn't produce either run, to
   avoid the model grading its own work favorably.
5. **Repeat** across multiple runs per scenario — a single run tells you
   almost nothing about consistency, and skills matter most for
   consistency, not peak performance on a lucky attempt.
6. **Record** results in `evaluations/results/README.md`, with the date,
   model/agent used, and number of runs — never as a one-off unlabeled
   number.

## What "good" looks like, concretely

Using `debugging-investigator` as the running example (see the root
[README](../README.md#see-it-in-action) for the short version):

- **Without the skill**, a capable agent asked "my API is occasionally
  returning duplicate payments" will often jump straight to a plausible-
  looking fix (e.g. "add a try/catch") without confirming *why* duplicates
  happen — because nothing in the prompt forces evidence-gathering first.
- **With the skill**, the same agent is instructed to reproduce, collect
  evidence, form and rank hypotheses, and only fix once a hypothesis is
  confirmed — which is the difference between a fix that addresses the
  actual race condition and one that happens to look reasonable.

This repository does not yet contain a recorded measurement of that
difference — see `evaluations/results/README.md`, which is intentionally
left as `NOT YET BENCHMARKED` until someone runs this process for real.
**Never fill that file in with an estimated or assumed number** — an
un-run benchmark is more honest than a fabricated one.
