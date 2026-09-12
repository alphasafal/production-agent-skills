# Example 2: Debug a Failure

**Skill**: [debugging-investigator](../../skills/debugging-investigator/)

## Try it

This example ships a real, runnable, reproducible bug — see
[`sample-app/`](sample-app/). Run it yourself first:

```bash
cd examples/02-debug-a-failure/sample-app
python3 reproduce_bug.py
```

Then ask an agent with `debugging-investigator` installed:

> "My endpoint occasionally creates duplicate orders. Investigate and fix it."

## What a correct run produces

`DEBUG_REPORT.md` — reproduction first, evidence, at least one explicitly
rejected hypothesis, a confirmed root cause naming the actual mechanism
(a check-then-act race — see `sample-app/BUG_SPOILER.md`), a minimal fix,
and a regression test that fails before the fix and passes after.

## Reference answer

[`skills/debugging-investigator/examples/duplicate-payment-investigation.md`](../../skills/debugging-investigator/examples/duplicate-payment-investigation.md)
walks the same failure mode end to end. `sample-app/BUG_SPOILER.md` has
this example's specific root cause and fix — try not to need it.

## Grading a real run

See [`evaluations/workflows/debugging-investigator.json`](../../evaluations/workflows/debugging-investigator.json).

## This is the demo used in the root README

See the root [README's "See it in action"](../../README.md#see-it-in-action)
section and [`docs/demo-guide.md`](../../docs/demo-guide.md) for the
before/after comparison methodology this example is built for.
