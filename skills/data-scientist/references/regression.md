# Regression

## Baseline

Mean (or median, if the target is skewed/has outliers) predictor. Report
both baseline and model MAE/RMSE so the improvement is visible in context,
not just as an abstract R².

## Choosing MAE vs. RMSE

- **MAE**: average absolute error, in the target's original units, robust
  to outliers. Prefer when large errors shouldn't be penalized
  disproportionately.
- **RMSE**: penalizes large errors more heavily (squared term). Prefer when
  large errors are actually worse in the real decision (e.g. a large
  underestimate of demand is much costlier than several small ones).
- Report both when unsure which the decision cares about more.

## Target transformation

A heavily right-skewed target (revenue, prices, durations) often models
better in log space — check the target's distribution before choosing.
If you log-transform, remember to transform predictions back before
computing MAE/RMSE in the original units, or the metric is not comparable
to the baseline computed in raw units.

## Residual analysis

Plot (or describe, if no plotting available) residuals vs. predicted value
and vs. key features. A pattern (not random scatter) indicates the model is
missing a systematic relationship — this is often more informative than
the aggregate R².

## Common failure to avoid

Reporting R² alone. R² can look good on a global fit while the model is
badly wrong for a specific important slice (see SKILL.md step 16, slice
analysis) — always pair it with the slice/error analysis steps.
