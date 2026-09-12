# Experiment Plan: <feature/hypothesis name>

## Hypothesis

State it as a falsifiable prediction: "If we do X, then Y will change by
Z, because <reasoning>."

## Design

- **Type**: A/B test | staged rollout | cohort comparison | qualitative
  feedback threshold
- **Randomization unit**: (user / session / account — match to where the
  effect occurs)
- **Sample size / duration**: (estimated, with the reasoning — see
  research-to-decision's `references/experiment-design.md` for how to
  size this properly)

## Primary metric and decision rule

The metric from `metrics-template.md`, and the specific threshold that
would trigger each decision (ship / iterate / abandon).

## Guardrails

Metrics that must not regress (from `metrics-template.md`).

## Risks to the experiment's validity

- Peeking/stopping early
- Novelty effects on user-facing changes
- Confounding concurrent launches

## Decision rule

- If primary metric hits target AND guardrails hold → ship
- If primary metric misses but guardrails hold → iterate / investigate why
- If any guardrail regresses meaningfully → stop and investigate before
  continuing regardless of the primary metric's result
