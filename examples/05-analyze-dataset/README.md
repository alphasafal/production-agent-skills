# Example 5: Analyze a Dataset

**Skill**: [data-scientist](../../skills/data-scientist/)

## Try it

Give an agent with `data-scientist` installed the fixture at
[`evaluations/fixtures/churn_sample.csv`](../../evaluations/fixtures/churn_sample.csv)
(15 synthetic customer rows with one deliberately leaky column and one
column with structured, non-random missingness) and ask:

> "Here's our customer dataset, build a model to predict churn."

You'll need the `data-scientist` extra installed to run its scripts
yourself: `pip install -e '.[data-scientist]'` from the repo root (or just
`pip install pandas numpy`).

## Try the scripts directly

```bash
python skills/data-scientist/scripts/generate_summary.py \
  evaluations/fixtures/churn_sample.csv --target churned --key customer_id
```

This alone should surface the `cancellation_reason` leakage column and the
structured missingness in `last_login_days_ago` — before any modeling.

## What a correct run produces

A findings summary that flags leakage before modeling, establishes a
naive baseline, and — given only 15 rows — explicitly notes the dataset is
too small for a reliable train/test split.

## Reference answer

[`skills/data-scientist/examples/customer-churn-walkthrough.md`](../../skills/data-scientist/examples/customer-churn-walkthrough.md)
walks a larger, similarly-shaped churn dataset through the full workflow.

## Grading a real run

See [`evaluations/workflows/data-scientist.json`](../../evaluations/workflows/data-scientist.json).
