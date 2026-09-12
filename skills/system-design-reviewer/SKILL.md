---
name: system-design-reviewer
description: >
  Reviews a proposed system or service architecture before implementation
  begins — requirements, API design, data model, storage, consistency,
  caching, queues/events, scaling, failure modes, security, observability,
  deployment, and cost. Use when evaluating a design doc, RFC, or proposed
  architecture for a new system/service, or when asked "does this design hold
  up," "what could go wrong with this architecture," or "review this system
  design." Do not use once implementation is already underway and the
  question is about the code itself (use production-code-review), or for
  reviewing an existing, already-built system's structure (use repo-architect).
license: MIT
compatibility: Text/diagram-based review. No filesystem or network access required unless the design doc lives in a connected tool.
metadata:
  category: engineering
  composes_with: [repo-architect, feature-to-production]
---

# Purpose

Stress-test a proposed architecture before code gets written, when design
mistakes are cheapest to fix.

# When to use

- A design doc, RFC, or architecture proposal exists and needs review before
  implementation starts.
- Asked to evaluate trade-offs between architectural approaches for a new
  system or a significant new component.

# When NOT to use

- The system is already built and the question is about its current code —
  that's `repo-architect` (to understand it) or `production-code-review`
  (to review a specific change to it).
- The "design" is really just a single function/class signature with no
  meaningful architectural surface (storage, scaling, failure modes) — a
  regular code review is enough.

# Required inputs

- The proposed design: a doc, RFC, diagram description, or the user's
  description of the intended architecture.
- Known constraints if available: expected scale, latency targets, team
  size/expertise, budget, existing systems it must integrate with.

If scale/constraints are missing, ask or state assumptions explicitly rather
than reviewing against an unstated, guessed bar.

# Workflow

1. **Clarify requirements** — what is this system actually supposed to do?
   If unclear, ask before reviewing against assumptions.
2. **Separate functional from non-functional requirements** — features vs.
   latency/availability/consistency/scale targets. Non-functional
   requirements are what most design reviews actually hinge on.
3. **Capture assumptions** — anything the design (or your review) takes for
   granted that isn't stated outright (traffic pattern, read/write ratio,
   data size, team's operational maturity).
4. **Estimate scale where possible** — rough numbers (requests/sec, data
   volume, growth rate) change which trade-offs are reasonable. State
   estimates as estimates, not facts.
5. **Review APIs** — consistency of the interface, versioning strategy,
   idempotency of mutating operations, pagination on collection endpoints.
6. **Review the data model** — entities, relationships, normalization
   choices, and whether the model matches actual access patterns.
7. **Review storage** — is the chosen storage technology matched to the
   access pattern (read-heavy vs write-heavy, relational vs. document vs.
   time-series, need for full-text/geo/vector search)?
8. **Review consistency** — what consistency model is assumed where, and
   does the design actually deliver it (e.g. "strongly consistent" claims
   over an eventually-consistent replica setup)?
9. **Review caching** — invalidation strategy specifically; a cache without
   a stated invalidation approach is a stale-data bug waiting to happen.
10. **Review queues/events** — delivery guarantees (at-least-once vs.
    exactly-once, and whether "exactly-once" is actually achievable given
    the stated mechanism), ordering guarantees, and consumer idempotency.
11. **Review scaling** — what's the bottleneck as load grows, and does the
    design's scaling story (horizontal scaling, sharding, read replicas)
    actually address that specific bottleneck?
12. **Review failure modes** — what happens when each dependency is slow or
    down? Partial failure handling, timeouts, retries, circuit breakers,
    graceful degradation.
13. **Review security** — authn/authz boundaries, data classification and
    where sensitive data flows, secrets handling, network exposure.
14. **Review observability** — can an operator tell this system is healthy
    or degraded in production? Metrics, logs, traces, alerting hooks.
15. **Review deployment** — rollout strategy, rollback plan, migration
    ordering for any schema/contract changes, blast radius of a bad deploy.
16. **Review cost** — rough infrastructure cost implications of the chosen
    approach, especially where a simpler/cheaper option would meet the
    actual requirements.
17. **Identify architectural risks** — synthesize the above into a ranked
    list of what's most likely to cause real problems.

# Tool & resource guidance

Ground every review point in the requirements and stated constraints from
step 1-4, not generic best practices applied without context — a design
appropriate for 100 req/s is not automatically wrong just because it
wouldn't survive 100k req/s if 100k was never a requirement.

- For step 12 (failure modes), read `references/failure-mode-patterns.md`
  to generate specific scenarios instead of generic resilience advice.
- For steps 8-9 (consistency, caching), read
  `references/consistency-and-caching-patterns.md` before judging whether
  the design's consistency claims and cache invalidation strategy hold up.

# Output contract

Produce `SYSTEM_DESIGN_REVIEW.md` with these sections:

- **Executive summary** — one paragraph: is this design sound, sound with
  changes, or not sound.
- **Assumptions** — what was assumed due to missing information.
- **Strengths** — what the design gets right, specifically.
- **Critical risks** — the highest-severity architectural risks found.
- **Failure scenarios** — specific "if X goes down/gets slow, then Y
  happens" scenarios.
- **Bottlenecks** — where the design will hit a scaling wall first.
- **Security concerns**
- **Scaling concerns**
- **Cost concerns**
- **Recommended changes** — concrete, prioritized.
- **Open questions** — things that need an answer before the design can be
  fully evaluated.

# Quality checks

- [ ] Every review dimension (steps 5-16) was actually considered, not
      silently skipped because nothing obvious jumped out.
- [ ] Failure scenarios are specific ("if the payment provider times out,
      the checkout request hangs indefinitely — no timeout is set"), not
      generic ("failure handling could be improved").
- [ ] Assumptions are stated, not silently baked into the review.
- [ ] Recommendations are prioritized, not a flat undifferentiated list.

# Edge cases

- **No numbers/scale given**: state reasonable assumptions explicitly and
  flag them in "Assumptions" and "Open questions" — don't silently pick a
  number and review as if it were given.
- **Design is intentionally simple for a low-stakes internal tool**: don't
  demand production-grade resilience the requirements don't call for — say
  what the trade-off is and let the team decide if it's acceptable.
- **Multiple competing design options presented**: review each against the
  same requirements and give a comparative recommendation, not just parallel
  independent reviews.

# References

See `examples/url-shortener-review.md` for a full worked example of the
output format applied to a small, concrete design.
