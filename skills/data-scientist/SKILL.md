---
name: data-scientist
description: >
  Runs an end-to-end structured tabular data science workflow: problem
  framing, schema/leakage/missingness checks, EDA, baseline before modeling,
  feature engineering, model comparison against the baseline, and error/slice
  analysis. Use when asked to analyze a dataset, build a predictive model,
  evaluate a model's performance, or investigate a data quality issue in
  tabular data. Do not use for pure data engineering/ETL with no analysis or
  modeling question, for unstructured data (images/audio/free text at scale)
  without a tabular framing, or when the task is answerable by a single
  summary statistic with no need for the full workflow — say so and just
  answer it.
license: MIT
compatibility: >
  Scripts require Python with pandas/numpy installed (see pyproject.toml's
  `data-scientist` extra). Needs filesystem access to the dataset file(s).
metadata:
  category: data
  composes_with: [product-manager, research-to-decision]
---

# Purpose

Turn "analyze this dataset" or "build a model" into a structured,
leakage-checked, baseline-anchored workflow instead of jumping straight to a
sophisticated model that may be solving the wrong problem or trained on a
false signal.

# When to use

- Asked to analyze a tabular dataset, build a predictive/classification
  model, or evaluate model performance.
- Asked to investigate a data quality issue (missingness, duplicates,
  suspicious distributions) in tabular data.

# When NOT to use

- The question is answerable with a single, simple aggregation ("what's the
  average order value last month") — just answer it; the full workflow is
  overkill.
- The task is ETL/pipeline engineering with no analysis or modeling
  question attached.
- **Never jump straight to a sophisticated model.** Always establish a naive
  baseline first (step 10) — a model that doesn't beat the baseline is a
  negative result worth reporting, not a failure to hide.

# Required inputs

- The dataset (file path or description of where it lives) and, if this is
  a modeling task, what's being predicted and why (the business/decision
  context — see step 1).

# Workflow

1. **Understand the decision/business problem** — what decision would this
   analysis or model actually inform? A model with no decision attached is
   a request to clarify, not a request to start training.
2. **Inspect the dataset** — shape, column types, a sample of rows. Use
   `scripts/profile_dataset.py`.
3. **Validate schema** — expected columns present, types sane, value ranges
   plausible. Mismatches here should stop the workflow, not be silently
   worked around.
4. **Identify the target** (if modeling) — confirm what column is being
   predicted and its distribution (class balance for classification, shape
   for regression).
5. **Detect leakage** — features that wouldn't be available at prediction
   time, or that are direct proxies/derivatives of the target. Use
   `scripts/check_leakage.py`; read `references/data-leakage.md` for the
   mechanisms to check beyond what the script catches.
6. **Check missingness** — patterns, not just totals (missing-at-random vs.
   missing-not-at-random matters for how to handle it). Use
   `scripts/check_missingness.py`.
7. **Check duplicates/outliers** — use `scripts/detect_duplicates.py`;
   investigate outliers rather than dropping them reflexively.
8. **EDA** — distributions, correlations with the target, relationships
   between key features. Let this inform, not replace, the hypotheses step.
9. **Hypotheses** — state what you expect to find and why, before or
   alongside EDA, so results can be interpreted against expectations.
10. **Choose the evaluation metric** — read `references/evaluation-metrics.md`
    and pick the metric that matches the actual decision from step 1, not
    the most common default. State why.
11. **Create a naive baseline** — for classification: majority class or a
    simple rule; for regression: mean/median predictor. This is
    non-negotiable — every later model is judged against it.
12. **Feature engineering** — only after the baseline exists, so its value
    is measurable.
13. **Train candidate models** — start simple (e.g. logistic/linear
    regression) before complex models; complexity must earn its keep against
    the next-simplest option, not just against the baseline.
14. **Compare with baseline** — use `scripts/evaluate_predictions.py`. If a
    model doesn't beat the baseline meaningfully, report that plainly.
15. **Error analysis** — look at what the best model gets wrong and why,
    not just the aggregate metric.
16. **Slice analysis** — check performance across meaningful subgroups
    (segments relevant to the decision from step 1); an aggregate metric can
    hide a subgroup where the model is actually harmful or useless.
17. **Interpretation** — connect findings back to the original decision.
18. **Recommendations** — what should actually change/happen as a result.

Read `references/classification.md`, `references/regression.md`, or
`references/time-series.md` depending on the problem type before step 10 —
each affects which metrics and validation strategy are valid, especially
for time-series, where standard k-fold cross-validation leaks future
information into the past.

# Tool & resource guidance

Run the deterministic scripts for anything they can determine exactly —
don't eyeball a `.describe()` output for missingness when
`scripts/check_missingness.py` gives an exact, reproducible answer.

```
python scripts/profile_dataset.py data.csv
python scripts/check_missingness.py data.csv
python scripts/detect_duplicates.py data.csv
python scripts/check_leakage.py data.csv --target outcome
python scripts/evaluate_predictions.py predictions.csv --y-true actual --y-pred predicted
python scripts/generate_summary.py data.csv --target outcome
```

Each script is standalone (`python scripts/<name>.py --help`) and requires
only pandas/numpy — install via `pip install -e '.[data-scientist]'` from
the repo root, or `pip install pandas numpy` directly.

Read `references/experiment-design.md` before recommending an A/B test or
similar experiment based on the analysis.

# Output contract

A findings summary covering: the decision context, key EDA findings, the
chosen metric and why, baseline performance, best model performance and
whether it beats baseline, error/slice analysis findings, and concrete
recommendations. For pure data-quality investigations (no modeling), the
same contract minus the modeling-specific sections.

# Quality checks

- [ ] A baseline was established before any "sophisticated" model, and the
      final comparison is against that baseline explicitly.
- [ ] Leakage was actively checked, not assumed absent.
- [ ] The chosen metric matches the actual decision, and that match is stated.
- [ ] Slice analysis was performed on at least one meaningful subgroup, not
      only an aggregate metric reported.
- [ ] If the task didn't actually need modeling, that was recognized and
      modeling was skipped rather than forced.

# Edge cases

- **Task is analysis-only, no modeling needed**: skip steps 10-16, keep
  1-9 and 17-18. Say explicitly that modeling wasn't warranted and why.
- **Dataset too small for a train/test split**: say so, use
  cross-validation or report the limitation rather than presenting an
  overfit single-split result as reliable.
- **Time-series data**: standard random train/test splitting leaks future
  data into training — read `references/time-series.md` before choosing a
  validation strategy.
- **Severe class imbalance**: accuracy is misleading as a metric here —
  read `references/evaluation-metrics.md` and `references/classification.md`.

# References

See `examples/customer-churn-walkthrough.md` for a full worked example of
this workflow end to end.
