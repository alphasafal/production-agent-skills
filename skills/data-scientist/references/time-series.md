# Time Series

## The single most common mistake: leaking the future into training

Standard random k-fold cross-validation puts future rows in the training
set and past rows in the test set for some folds — the model then gets
evaluated on a task it could never actually perform in production (predict
the past using the future). This inflates every metric.

**Use instead**: a rolling-origin / walk-forward split — train on data up
to time T, validate on T+1..T+k, then roll T forward. Never shuffle rows
across the time axis before splitting.

## Feature engineering considerations

- Lag features and rolling aggregates (rolling mean/std) must only use data
  strictly before the prediction time for each row — check the window
  doesn't accidentally include the current or future row.
- Any external join (e.g. joining in "current" customer status) can leak
  future information if the joined table reflects a later state than what
  was known at the row's timestamp — this is a common, easy-to-miss leakage
  path that `scripts/check_leakage.py`'s correlation heuristic will not
  reliably catch (the leaked column may not correlate highly if the future
  state is noisy — the leak is about *timing*, not correlation strength).

## Baseline

For time series, "naive" baselines are stronger than in i.i.d. data: e.g.
"predict the same value as the last observed period" (naive forecast) or
seasonal naive (same period last cycle). A model must beat this, not just
beat a plain mean predictor.

## Stationarity

Check whether the series has trend/seasonality; many models assume (or
perform much better on) a stationary series. Note if differencing or
deseasonalizing was applied, since it changes how to interpret error
metrics (errors on differenced data aren't directly comparable to errors
on the raw series).
