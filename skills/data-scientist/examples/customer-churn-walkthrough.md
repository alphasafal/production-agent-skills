# Worked example: customer churn analysis

**Prompt:** "Here's our customer dataset — build a model to predict churn."

Abridged walkthrough:

1. **Decision context**: clarified with the user — the model will feed a
   monthly list of at-risk customers to the retention team, who can only
   realistically call ~200 customers/month. This matters: it points toward
   a ranking/precision@200 framing, not raw accuracy.
2. **Profile** (`profile_dataset.py`): 40,000 rows, 22 columns, target
   `churned` is ~12% positive — imbalanced.
3. **Schema validation**: `signup_date` parses as a date, `plan_type` has 3
   expected categories, no unexpected values found.
4. **Leakage check** (`check_leakage.py --target churned`): flagged
   `cancellation_reason` — a deterministic 1:1 encoding of churned==1 rows
   (it's null for active customers). Dropped: it's a *consequence* of
   churn, not a predictor of it, per `references/data-leakage.md`.
5. **Missingness** (`check_missingness.py`): `last_login_days_ago` missing
   for 3% of rows, co-occurring with `plan_type == 'trial'` — these are
   trial users who never logged in, not random noise; imputed as a large
   sentinel value rather than the column mean.
6. **Duplicates** (`detect_duplicates.py --key customer_id`): none found.
7. **EDA**: churned customers have notably higher `support_tickets_30d` and
   lower `feature_adoption_score` — consistent with the hypothesis that
   disengagement precedes churn.
8. **Metric choice**: given the 200-customer/month capacity constraint,
   chose **precision@200** (of the top 200 customers ranked by predicted
   churn risk, what fraction actually churn) over plain accuracy or AUC.
9. **Baseline**: majority-class baseline (always predict "not churned") has
   0% recall on churn by construction — reported as the floor, and a
   "random 200 customers" baseline for precision@200 (~12%, matching base rate).
10. **Model**: logistic regression first (interpretable, fast), then
    gradient boosting. Gradient boosting's precision@200 (41%) meaningfully
    beat both the random baseline (12%) and logistic regression (29%).
11. **Error analysis**: gradient boosting under-flagged a segment of
    high-tenure customers who churned suddenly after a pricing change —
    the model had little training signal for this newer pattern.
12. **Slice analysis**: precision@200 for `plan_type == 'enterprise'`
    customers was notably lower (22%) than for `plan_type == 'self-serve'`
    (48%) — enterprise churn has different drivers not well captured by
    current features.
13. **Recommendation**: ship the gradient boosting model for self-serve
    customers now; flag enterprise churn as needing separate features
    (e.g. contract renewal date, account health score) before it's
    reliable enough to act on.
