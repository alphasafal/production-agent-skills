# Data Leakage

`scripts/check_leakage.py` catches mechanical signals (high correlation,
suspicious names, deterministic encodings). It cannot catch leakage that's
about **timing** or **process**, which requires understanding how the data
was actually collected — check these manually:

## Timing leakage

A feature that would not actually be available at prediction time, even if
it doesn't correlate suspiciously with the target. Example: predicting
loan default using a feature computed from the loan's full repayment
history — that history doesn't exist yet at the moment the prediction
would actually be made in production.

**Check**: for every feature, ask "would this value actually be known at
the moment we'd need to make this prediction in production?"

## Train/test contamination

Rows that are duplicated or near-duplicated across the train and test
split (common with grouped data — see `references/classification.md` on
group k-fold), or preprocessing (e.g. scaling, imputation, feature
selection) fit on the full dataset before splitting instead of fit on
train and applied to test.

**Check**: was any statistic (mean for imputation, scaler parameters,
selected features) computed using the test set at all?

## Target leakage via a proxy

A feature that isn't the target itself but is causally downstream of it —
e.g. "number of collections calls made" as a feature for predicting loan
default; calls are made *because* the loan defaulted, so the feature only
exists in cases that already are (or are heavily correlated with) positive
labels.

**Check**: for each strong feature, ask whether it's a cause of the target
or a consequence of it.

## Sampling leakage

If the dataset was constructed by filtering on a condition related to the
target (e.g. only including customers who churned or a matched sample),
that filtering process itself needs to be understood before trusting any
metric — the model may be learning the sampling process, not the real signal.
