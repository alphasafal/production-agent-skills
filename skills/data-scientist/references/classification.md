# Classification

## Class imbalance changes almost everything

If the minority class is under ~10-20%, accuracy is close to meaningless
(a model that always predicts the majority class can score 90%+ while being
useless). Use precision/recall/F1 per class, or PR-AUC, instead — see
`evaluation-metrics.md`.

## Baseline

Majority-class prediction. Report its accuracy AND its per-class precision/
recall (it will have zero recall on the minority class) so the comparison
is honest, not just a headline accuracy number.

## Validation strategy

- Stratified k-fold (preserves class ratio in each fold) for anything beyond
  the most trivial imbalance.
- Group k-fold instead of plain k-fold if multiple rows belong to the same
  entity (e.g. multiple transactions per customer) and that entity
  shouldn't appear in both train and test — otherwise this is a leakage
  path (`scripts/check_leakage.py`'s correlation check won't catch this
  kind — it's about row grouping, not column values).

## Thresholding

Most classifiers output a probability; the 0.5 cutoff is a default, not a
law. If the decision (step 1 in SKILL.md) has asymmetric costs (a false
negative is worse than a false positive, or vice versa), choose the
threshold based on that cost structure, and say so explicitly.

## Common failure to avoid

Reporting only accuracy on an imbalanced problem and calling a model
"good" because it beats a majority-class baseline by a tiny margin while
having near-zero recall on the class that actually matters for the decision.
