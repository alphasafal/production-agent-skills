# Experiment Design (for recommendations that lead to an A/B test)

When an analysis's recommendation is "launch this and measure impact,"
apply this before proposing the experiment.

## Define the decision the experiment will make

State the specific decision ("ship variant B to 100% of users") and the
specific metric that will make it, before designing the test — not after
seeing initial results (this prevents metric-shopping / p-hacking after
the fact).

## Minimum detectable effect and sample size

State the smallest effect size worth detecting (tied to the business
decision, e.g. "a 2% lift in conversion is worth shipping") and estimate
the sample size/duration needed to detect it at a reasonable power
(commonly 80%) and significance level (commonly 0.05) — don't run a test
sized to detect an effect much smaller than what would actually change the
decision; it just wastes time.

## Randomization unit

Match the randomization unit to where the effect and any interference
occurs (user vs. session vs. account) — randomizing at the wrong level
(e.g. per-request for an effect that plays out per-user over multiple
sessions) invalidates the statistics.

## Guardrail metrics

Define metrics that must not regress (e.g. latency, error rate, revenue)
alongside the primary metric, decided before launch, so a "win" on the
primary metric isn't accepted despite quietly breaking something else.

## Common pitfalls to flag if seen

- Peeking at results and stopping early once significance is hit (inflates
  false-positive rate).
- Running multiple variants/metrics and reporting only the one that hit
  significance (multiple-comparisons problem).
- Novelty effects: a short test window may show inflated interest in a new
  variant that fades — flag if the recommended launch is based on a very
  short test window for a user-facing UI change.
