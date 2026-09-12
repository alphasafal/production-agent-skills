---
name: production-code-review
description: >
  Performs structured, senior-level review of a code change (diff or PR)
  across correctness, security, reliability, error handling, concurrency,
  performance, data integrity, API contracts, maintainability, observability,
  tests, and backward compatibility. Ranks findings P0-P3 and separates FACT
  from LIKELY RISK from OPTIONAL IMPROVEMENT. Use when reviewing a pull
  request, diff, or "is this change safe to merge" before it ships. Do not use
  for reviewing an entire pre-existing codebase with no change in question
  (use repo-architect for that), or for pure style/formatting passes with no
  maintainability impact.
license: MIT
compatibility: Needs read access to the diff/PR and enough surrounding code to judge impact. No network required.
metadata:
  category: engineering
  composes_with: [feature-to-production, debugging-investigator]
---

# Purpose

Give a change a review with the rigor of a senior engineer who reads for
consequences, not just syntax — and who is explicit about what's a proven
fact versus a plausible risk versus a nice-to-have.

# When to use

- A diff or pull request is ready (or claimed ready) to merge.
- Explicitly asked "review this," "is this safe to ship," or similar.
- After `feature-to-production` implements a change, as its review stage.

# When NOT to use

- No specific change exists yet — reviewing an entire codebase's health is
  `repo-architect`'s job, not this skill's.
- The only concern is naming/formatting with no bearing on correctness,
  security, or long-term maintainability — don't manufacture findings.

# Required inputs

- The diff, PR, or set of changed files.
- Enough surrounding code (call sites, related tests, schema) to judge real
  impact rather than reviewing the diff in isolation.

# Workflow

1. Read the full diff before forming any opinion — do not review hunk by
   hunk without the surrounding context of what the change is trying to do.
2. For each of the 12 dimensions below, actively check for issues — don't
   wait for something to jump out. Absence of a finding in a dimension is
   itself worth noting mentally, not proof there's nothing there.
3. For each candidate finding, gather the evidence (the actual line, the
   actual call site, the actual test — or lack of one) before writing it up.
4. Classify each finding: **FACT** (directly demonstrable from the code as
   written), **LIKELY RISK** (a plausible failure mode given the evidence,
   not certain), or **OPTIONAL IMPROVEMENT** (would be better, not a defect).
5. Assign severity per the rubric below.
6. Write up findings ranked most severe first, each with severity,
   file/location, evidence, impact, and a recommended fix.
7. Summarize: is this safe to merge as-is, safe with the P0/P1 items fixed,
   or not safe to merge.

## Review dimensions

Correctness · Security · Reliability · Error handling · Concurrency ·
Performance · Data integrity · API contracts · Maintainability ·
Observability · Tests · Backward compatibility

- For security-sensitive changes (auth, input handling, secrets, injection
  surfaces), read `references/security-checklist.md`.
- For anything touching shared state, async code, hot paths, or resource
  usage, read `references/concurrency-and-performance.md`.
- For anything changing a public API, DB schema, or wire format, read
  `references/api-contracts-and-compatibility.md`.

## Severity rubric

- **P0 — critical**: data loss/corruption, security vulnerability, or a
  correctness bug on a common path. Blocks merge.
- **P1 — high**: correctness bug on an edge case, missing error handling
  that causes a crash/hang, or a reliability gap in a critical path.
  Should block merge or ship with an explicit, informed exception.
- **P2 — medium**: real but bounded impact — a performance regression, a
  maintainability problem that will cost real time later, a test gap on a
  non-trivial path.
- **P3 — improvement**: worth doing, not blocking — clarity, minor
  duplication, a more idiomatic approach.

# Tool & resource guidance

Read actual call sites and tests, don't assume behavior from function names.
When a finding depends on how a function is used elsewhere, grep for its
usages rather than asserting impact from the diff alone.

# Output contract

A findings list, ranked P0 first, each with:

- **Severity** (P0-P3) and **classification** (FACT / LIKELY RISK / OPTIONAL IMPROVEMENT)
- **File/location**
- **Evidence** — the actual code/behavior that supports the finding
- **Impact** — what happens if this ships as-is
- **Recommended fix**

Followed by a one-paragraph merge recommendation.

# Quality checks

- [ ] Every finding has file/location and evidence — no vague "this could be
      a problem somewhere."
- [ ] FACT findings are actually demonstrable, not classified as fact out of
      confidence alone.
- [ ] No P3 findings are presented as blocking; no real P0/P1 is downgraded
      to keep the review friendly.
- [ ] Style-only observations are excluded unless they materially affect
      maintainability (e.g. a pattern that will cause real bugs when copied).
- [ ] The merge recommendation matches the severities found — don't say
      "safe to merge" alongside an unresolved P0.

# Edge cases

- **Large diff spanning unrelated concerns**: note that as a P2/P3
  maintainability/process finding (should have been split), but still
  review the actual content fully.
- **No tests exist for the changed path**: this is a finding (severity
  depends on how critical the path is), not a blocker to reviewing the
  rest of the diff.
- **Change is trivial (e.g. a config value bump)**: say so plainly and give
  a short review rather than manufacturing findings across all 12 dimensions.
- **Reviewer disagrees with an existing architectural pattern the diff
  merely follows**: don't flag pre-existing patterns as new findings unless
  the diff makes the specific instance worse.

# References

See `examples/idempotency-key-review.md` for a full worked example of the
output format, including severity classification and a merge recommendation.
