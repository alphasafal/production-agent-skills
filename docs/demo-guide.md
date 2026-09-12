# Demo Guide

Everything needed to run or record a demo of this repository lives in
`demos/`:

- [`demos/demo-prompts.md`](../demos/demo-prompts.md) — one copy-pasteable,
  tested (`positive-obvious`) prompt per skill.
- [`demos/expected-behavior.md`](../demos/expected-behavior.md) — what a
  correct run of each prompt should look like, and the specific red flag
  that indicates the skill wasn't actually followed.
- [`demos/recording-script.md`](../demos/recording-script.md) — a full
  5-7 minute video script, beat by beat.

## Quickest possible demo (2 minutes, no recording)

```bash
python scripts/list_skills.py
python scripts/inspect_skill.py debugging-investigator
python scripts/install_skills.py --skill debugging-investigator --target ./.claude/skills --dry-run
```

Then paste the `debugging-investigator` prompt from `demos/demo-prompts.md`
into an agent session with the skill installed.

## The strongest single demo: before vs. after

`examples/02-debug-a-failure/sample-app/` has a real, deterministic,
reproducible bug. This is the one demo that shows the skill actually
changing behavior rather than just existing:

1. Run the sample app's bug-reproduction script yourself first (see its
   `README.md`) so you know what "confirmed root cause" should look like —
   `BUG_SPOILER.md` has the answer, but try not to need it.
2. Ask an agent **without** `debugging-investigator` installed: "My
   endpoint occasionally creates duplicate orders. Investigate and fix it."
   Watch whether it reproduces first or guesses first.
3. Install the skill, ask the identical prompt, and compare.
4. Grade both against `evaluations/workflows/debugging-investigator.json`'s
   `required_behaviors`.

This is also exactly the methodology in
[`docs/evaluating-skills.md`](evaluating-skills.md) — a demo and a real
evaluation run are the same procedure at different levels of rigor.

## Recording a video

Follow `demos/recording-script.md` directly — it's written to be read
almost verbatim, with natural pause points at each section break.
