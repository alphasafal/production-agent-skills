---
name: product-manager
description: >
  Turns an ambiguous product idea or feature request into a validated,
  right-sized product plan: problem definition, target user, jobs-to-be-done,
  assumptions and risk ranking, a minimal MVP scope, user stories, success
  metrics, and a PRD. Use when asked to scope a new feature or product idea,
  write a PRD, define an MVP or the minimum version to launch first, decide what
  to build next, or turn a vague request ("we should have X") into something
  buildable. Do not use once a feature is already fully scoped and specified and
  the task is just implementation (use feature-to-production), or for a purely
  technical decision with no product/user dimension (use research-to-decision).
license: MIT
compatibility: Text-based planning skill. No filesystem/network access required beyond reading any existing product docs the user provides.
metadata:
  category: product
  composes_with:
    - data-scientist
    - research-to-decision
    - feature-to-production
---

# Purpose

Prevent premature feature explosion by forcing an idea through problem
definition and risk ranking before scope is decided — so the MVP is the
smallest thing that actually tests the riskiest assumption, not a wish list.

# When to use

- A vague or ambitious product idea needs to become a scoped, buildable plan.
- Asked to write a PRD, define an MVP, or turn "we should build X" into
  user stories and success metrics.

# When NOT to use

- The feature is already fully specified (clear scope, clear acceptance
  criteria) — go straight to `feature-to-production`.
- The question is a pure technology choice with no user-facing product
  dimension — that's `research-to-decision`.

# Required inputs

- The idea or request, however rough.
- Whatever's known about the target user/context — ask if genuinely unknown
  rather than inventing a persona wholesale.

# Workflow

1. **Idea/request** — capture it as stated, without immediately jumping to
   solution details.
2. **Problem definition** — what problem is this actually solving, for whom?
   If the request is already a solution ("add a dashboard"), work backward
   to the underlying problem before accepting the solution as given.
3. **Target user** — who specifically has this problem? Avoid "everyone."
4. **Jobs-to-be-done** — what is the user actually trying to accomplish,
   independent of any specific feature?
5. **Pain / current alternatives** — how do they solve this today, and
   what's wrong with that? A problem with no real current pain is a weak
   foundation for a feature.
6. **Assumptions** — list what must be true for this to be worth building
   (usage frequency, willingness to change behavior, technical feasibility).
7. **Risk ranking** — rank assumptions by (a) how likely they are to be
   wrong and (b) how costly it is if they are. The riskiest, cheapest-to-test
   assumption drives the MVP scope — not the most exciting feature.
8. **Hypotheses** — turn the riskiest assumptions into falsifiable
   statements ("users will complete checkout 20% more often if we remove
   this step") that the MVP/experiment can actually test.
9. **MVP scope** — the smallest version that tests the top hypothesis.
   **Actively resist scope growth**: if a feature doesn't test the
   hypothesis or serve the core job-to-be-done, cut it from v1 regardless
   of how easy or appealing it seems.
10. **User stories** — concrete, testable stories for the MVP scope only.
11. **Success metrics** — how will you know if the hypothesis was right?
    Tie directly to the hypothesis from step 8, not a vanity metric.
12. **Experiment design** — how the MVP will actually be evaluated (A/B
    test, cohort comparison, qualitative feedback threshold) — see
    `research-to-decision`'s `references/` for rigor on this if it's a
    formal experiment.
13. **PRD** — the durable artifact combining the above (see output contract).

# Tool & resource guidance

If usage/behavioral data already exists that bears on the risk ranking
(step 7) or could establish a real baseline for the success metric (step
11), that's a `data-scientist` task — don't guess at numbers a dataset
could actually answer.

# Output contract

Using the templates in `assets/`:

- **PRD** (`assets/prd-template.md`) — problem, users, MVP scope, stories,
  metrics, non-goals.
- **User stories** (`assets/user-story-template.md`) for each MVP-scope story.
- **Success metrics** (`assets/metrics-template.md`).
- **Experiment plan** (`assets/experiment-template.md`) if a formal
  test/rollout is warranted.
- **Decision log** (`assets/decision-log-template.md`) for major scope
  decisions and why they were made (especially what was cut and why).

# Quality checks

- [ ] The MVP scope is traceable to the single riskiest hypothesis, not a
      collection of "nice to have while we're at it" features.
- [ ] Every user story in scope is testable and tied to the core job-to-be-done.
- [ ] Success metrics are specific and tied to the hypothesis, not generic
      ("increase engagement").
- [ ] At least one thing was explicitly cut from scope and recorded in the
      decision log — if nothing was cut, scope discipline probably wasn't
      actually applied.

# Red flags

Stop and correct course if any of these are true:

- The PRD starts from the requested solution, and the problem statement was back-filled to fit it.
- The target user is "everyone", "users", or "small businesses" with no narrower segment.
- The MVP includes a feature that doesn't test the top hypothesis.
- The success metric is a vanity metric (sign-ups, page views) unconnected to the hypothesis.
- Assumptions are listed but not ranked by likelihood-of-wrong and cost-if-wrong.
- There is no way described to learn the MVP failed.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "It's a small extra feature, just add it to v1." | Small extras compound into a late, unfocused MVP. If it doesn't test the hypothesis, it goes to the later list. |
| "The stakeholder asked for exactly this, so the problem is clear." | A request is a proposed solution. Work back to the problem first — often a smaller solution solves it. |
| "We'll figure out metrics after launch." | Metrics chosen after launch get picked to look good. Define success before building. |
| "Users definitely want this." | That's the riskiest assumption in most PRDs. Rank it, and design the MVP to test it cheaply. |
| "This is too small to need a PRD." | Then the PRD is short. The problem, user, hypothesis and metric still need to exist, even as four lines. |

# Edge cases

- **User already has a fully-formed feature spec**: don't force the full
  workflow — validate the MVP-scoping and risk-ranking steps briefly, then
  move to `feature-to-production`.
- **No clear target user yet**: make defining one step 1 of the actual
  deliverable rather than picking one arbitrarily and proceeding.
- **Stakeholder pressure for a large v1**: state the risk-ranking-based
  case for the smaller MVP explicitly in the decision log rather than
  silently capitulating to scope growth.

# References

See `examples/collaborative-playlist-prd.md` for a full worked example.
