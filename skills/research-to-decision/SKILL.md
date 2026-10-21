---
name: research-to-decision
description: >
  Turns research into an auditable technical or product decision: defines the
  decision and constraints, gathers evidence with sources, separates evidence
  from assumption, compares alternatives against explicit criteria, and produces
  an ADR. Use when choosing between technologies, tools, vendors, or providers
  ("Kafka vs SQS", "REST or GraphQL", "build vs buy"), deciding whether a switch
  is worth it, settling a choice a team keeps debating, documenting the
  reasoning behind a decision already made, or when asked to "research this and
  recommend one." Do not use for implementing the chosen option (that's a
  separate skill), or for open-ended research with no decision to make at the
  end.
license: MIT
compatibility: >
  Benefits from web research/search tools for external evidence; without
  them, state that sourced claims could not be verified rather than
  fabricating citations.
metadata:
  category: research
  composes_with:
    - product-manager
    - data-scientist
    - system-design-reviewer
---

# Purpose

Make the reasoning behind a decision inspectable later: what was compared,
what evidence supported it, what was assumed, and why the choice was made —
not just the conclusion.

# When to use

- Choosing between concrete alternatives (technologies, vendors, approaches)
  with real trade-offs.
- Asked to "research X and recommend one" or to document why a decision was
  made.

# When NOT to use

- The task is open-ended research with no decision at the end ("what's the
  state of the art in X") — that's fine to do, but skip the decision-matrix/
  ADR machinery; just report findings.
- The "decision" has only one reasonable option — say so plainly instead of
  manufacturing a comparison.

# Required inputs

- The decision to be made, stated specifically.
- Known constraints (budget, timeline, team expertise, existing systems).

If the decision is vague ("should we improve our infra"), narrow it to a
specific, answerable question before proceeding.

# Workflow

1. **Define the decision** — state it as a specific question with a finite
   set of options, not an open-ended topic.
2. **Capture constraints** — budget, timeline, team skills, compliance,
   existing systems it must integrate with. These often eliminate options
   before evidence-gathering even starts.
3. **Define evaluation criteria** — the dimensions that actually matter for
   this decision (e.g. operational complexity, cost at expected scale,
   ecosystem maturity, team familiarity), agreed before comparing options so
   criteria aren't picked to justify a pre-existing preference.
4. **Collect reliable evidence** — use available research/web tools for
   external claims (official docs, benchmarks, credible technical sources).
   Prefer primary sources over blog-post summaries when possible.
5. **Separate evidence from assumption** — every claim is either backed by
   a source/citation or explicitly marked as an assumption. Never blur the two.
6. **Compare alternatives** — score or rank each option against the
   criteria from step 3, using the evidence from step 4.
7. **Identify trade-offs** — no option wins on every criterion; state what's
   given up by choosing each one.
8. **Record uncertainties** — what wasn't verifiable, what could change the
   recommendation if it turned out to be wrong.
9. **Recommend a decision** — the option that best fits the criteria and
   constraints, with the reasoning explicit.
10. **Create an ADR** — the durable record (see output contract).

# Tool & resource guidance

- Use web search/fetch tools when available for external technical claims
  (performance characteristics, pricing, community/ecosystem maturity).
  **Never fabricate a citation** — if a claim can't be verified, mark it as
  an assumption or state it plainly as unverified.
- If the decision has a heavy technical-architecture dimension (e.g.
  choosing a database or messaging system), consider whether
  `system-design-reviewer` should evaluate the shortlisted option's fit
  before finalizing.
- If the decision depends on user/usage data, `data-scientist` may need to
  run first to produce that evidence.

# Output contract

Three artifacts:

- **RESEARCH.md** — raw findings with source attribution for every external
  factual claim.
- **DECISION_MATRIX.md** — options × criteria, scored, with the evidence
  each score is based on.
- **ADR.md** — using `assets/adr-template.md`: context, decision, options
  considered, consequences (including trade-offs given up).

# Quality checks

- [ ] Every external factual claim has a source, or is explicitly marked as
      an assumption/unverified — no invented citations.
- [ ] Criteria were defined before scoring, not reverse-engineered from a
      pre-decided answer.
- [ ] The recommendation explicitly states what's traded away, not just
      what's gained.
- [ ] The ADR is understandable on its own, without the full research doc,
      to someone reading it in a year.

# Red flags

Stop and correct course if any of these are true:

- A factual claim (a price, a limit, a benchmark) has no citation and isn't marked as an assumption.
- Evaluation criteria were written after you'd seen which option wins on them.
- A citation points to a source you didn't actually open.
- One option wins on every criterion with no stated trade-off.
- The recommendation doesn't mention the constraints captured earlier (budget, team skills, compliance).
- There is no "what would change this decision" section.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "Everyone knows Postgres / Kafka / X is better for this." | Then it's easy to source. Popular wisdom is an assumption until a primary source backs it for *this* workload. |
| "I'm fairly sure about this number, I'll state it." | Confidence isn't a citation. Mark it as an assumption or verify it — never present it as sourced fact. |
| "We already know what we want; just write the ADR." | An ADR that records a pre-made choice without the alternatives and trade-offs is a press release. Record what was given up. |
| "The blog post summarizes the docs well enough." | Summaries drift and go stale. Prefer the primary source, especially for limits and pricing. |
| "There's too much uncertainty to recommend anything." | Recommend the best option under stated uncertainty and say what would flip it. "It depends" is not a decision. |

# Edge cases

- **No research tools available**: proceed using existing knowledge, but
  mark every claim's confidence level and recommend the user verify
  time-sensitive facts (pricing, version-specific behavior) independently.
- **Only one viable option given the constraints**: state that plainly in
  the ADR rather than inventing a false comparison.
- **Decision is highly reversible/low-stakes**: keep the ADR brief — the
  rigor should scale with the cost of being wrong.

# References

See `references/adr-quality.md` for what separates a useful ADR from a
box-checking one, `references/evidence-sourcing.md` for how to handle
claims that can't be fully verified, and
`examples/kafka-vs-sqs-decision.md` for a full worked example.
