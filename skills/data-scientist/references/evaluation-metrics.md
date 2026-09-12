# Choosing an Evaluation Metric

Pick the metric that matches the decision from SKILL.md step 1 — not the
most familiar default. State the choice and why.

## Classification

| Situation | Prefer |
|---|---|
| Balanced classes, errors equally costly | Accuracy |
| Imbalanced classes | Precision/recall/F1 per class, PR-AUC |
| Ranking/screening use case (e.g. top-K review queue) | AUC-ROC or precision@K |
| False positives and false negatives have different costs | A cost-weighted metric, or report both precision and recall separately rather than collapsing to one number |

## Regression

| Situation | Prefer |
|---|---|
| Errors in original units matter, outlier-robust | MAE |
| Large errors are disproportionately costly | RMSE |
| Comparing fit across different-scale targets | R² (but pair with MAE/RMSE — see regression.md) |
| Target spans orders of magnitude | MAPE or metrics computed in log space |

## General rule

Report the chosen metric AND at least one other for context (e.g. accuracy
alongside F1, or MAE alongside R²) — a single number, without the baseline
comparison from SKILL.md steps 11/14, is not enough to judge whether a
model is actually useful for the decision it's meant to inform.
