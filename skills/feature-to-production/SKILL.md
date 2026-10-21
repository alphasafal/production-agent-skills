---
name: feature-to-production
description: >
  Guides a software feature from a clarified requirement through implementation
  to production readiness: acceptance criteria, repository understanding,
  smallest-viable design, tests, implementation, verification, review,
  security/performance checks, documentation, and a deployment/rollback plan.
  Use when asked to build, add, implement, or ship a feature end to end —
  including implementing a fully specified ticket or spec, adding a capability
  to an API or app, or taking work "all the way to done" — not just write a
  snippet. Do not use for a one-line fix (use debugging-investigator if it's a
  bug) or when the requirement itself is still vague (use product-manager first
  to scope it).
license: MIT
compatibility: Needs filesystem/shell access to implement and test. No network required beyond what the project's own tests/build need.
metadata:
  category: engineering
  composes_with:
    - repo-architect
    - production-code-review
    - debugging-investigator
    - product-manager
---

# Purpose

Carry a clarified requirement to a production-ready change without skipping
the steps that make it safe: understanding the codebase, designing the
smallest viable change, testing it, and leaving a deployment/rollback plan —
not just writing code that runs once locally.

# When to use

- A specific, reasonably well-defined feature or change needs to go from
  requirement to shipped.

# When NOT to use

- The requirement is still vague/unscoped — run `product-manager` first.
- It's a one-line fix with an already-known cause — just make the change
  and add/run a regression test; this skill's full ceremony isn't needed.
- It's a bug with an unknown cause — that's `debugging-investigator`, not
  this skill (this skill assumes the *what* is known; only the *how* is
  being worked out).

# Required inputs

- A requirement with clear (or clarifiable) acceptance criteria.
- Repository access.

# Workflow

This skill orchestrates its own steps plus, at defined points, hands off to
other skills that own that specific stage. **Do not have those skills
invoke this skill back** — the flow is one-directional to avoid recursive
invocation.

1. **Requirement** — restate what's being asked in your own words to
   surface ambiguity early.
2. **Clarify acceptance criteria** — if not already explicit, define what
   "done" looks like concretely enough to test against. If the requirement
   is too vague to do this, that's a signal to hand off to `product-manager`
   rather than guessing.
3. **Inspect the repository** *(owned by `repo-architect` if this is an
   unfamiliar codebase or area)* — understand what exists before designing
   the change. Skip this step's full ceremony if you already have a solid
   model of the relevant area from earlier in the session.
4. **Understand current architecture** in the specific area being changed —
   what module, what existing patterns, what would a consistent change
   look like.
5. **Design the smallest viable change** — the minimal modification that
   satisfies the acceptance criteria. Resist bundling in unrelated
   improvements or speculative generalization.
6. **Identify affected interfaces** — what other code calls into or depends
   on what's being changed; check for all call sites, not just the obvious one.
7. **Implementation plan** — sequence of concrete steps, including what
   tests will be added before or alongside the code.
8. **Tests** — write tests for the acceptance criteria before or alongside
   implementation; a feature isn't done when it works once manually, it's
   done when a test proves it.
9. **Implementation** — build the smallest viable change from step 5.
10. **Verification** — run the tests, and manually exercise the feature if
    testable interactively (e.g. via a running dev server, per the `run`
    skill's approach if available). If tests unexpectedly fail here and the
    cause isn't obvious, hand off to `debugging-investigator` rather than
    guessing at fixes.
11. **Code review** *(owned by `production-code-review`)* — review the
    resulting diff across correctness, security, reliability, and the
    other review dimensions before considering this done.
12. **Security/performance checks** — covered by step 11's review
    dimensions; call out explicitly if this change touches auth, user
    input, or a hot path, since those warrant extra scrutiny.
13. **Documentation** — update any docs/README/comments that are now stale
    because of this change; don't leave documentation silently out of sync.
14. **Deployment checklist** — migration ordering, feature flags, config
    changes needed, and what to monitor immediately after deploy.
15. **Rollback strategy** — how to revert safely if this causes a problem
    in production (a flag to flip, a migration that's safely reversible, or
    a plain revert if the change has no persisted-state implications).

# Tool & resource guidance

- Unfamiliar repo or area → `repo-architect` for step 3.
- After implementation → `production-code-review` for step 11.
- Tests fail unexpectedly and the cause isn't immediately obvious →
  `debugging-investigator` rather than trial-and-error edits.
- Requirement too vague to define acceptance criteria → `product-manager`
  before proceeding further with this skill.

Each handoff is one-directional: the called skill does its job and returns
control here. Don't let a called skill re-invoke `feature-to-production`.

# Output contract

- The implemented change, with tests.
- A short implementation summary: what changed, why, and how it was verified.
- A deployment checklist (migrations, flags, config, what to monitor).
- A rollback plan.
- Updated documentation where the change made existing docs stale.

# Quality checks

- [ ] Every acceptance criterion has a corresponding test.
- [ ] The change is traceable to the smallest viable design — no
      unrelated scope bundled in.
- [ ] All call sites of any changed interface were checked, not just the
      one this task originated from.
- [ ] A rollback plan exists and is specific to this change, not generic
      boilerplate ("just revert the commit" is fine only when there's no
      persisted-state/migration complication — say so explicitly if true).
- [ ] Documentation affected by the change was actually updated.

# Red flags

Stop and correct course if any of these are true:

- You started writing implementation code and the acceptance criteria still aren't written down.
- The diff touches files unrelated to the acceptance criteria.
- "Done" was declared after a manual check, with no test asserting the new behaviour.
- You are about to report the change as done and no review pass (step 11) has been run on the diff.
- A test failed and you changed code until it passed without knowing why it failed.
- Only the obvious call site of a changed interface was checked.
- The change touches a schema or persisted data and there is no rollback plan.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "The requirement is clear enough, skip acceptance criteria." | If it's clear, writing it down takes a minute. If it isn't, you just found the ambiguity before building the wrong thing. |
| "I'll add tests after it works." | Tests written after are shaped by the code, not the requirement, and often don't get written. Test the criteria alongside the code. |
| "While I'm here I'll refactor this module." | Out-of-scope changes widen review and rollback blast radius. Note it; ship the smallest viable change. |
| "The tests pass, so a review pass is redundant." | Tests check what you thought of. Review is for what you didn't: the unprotected entry point, the unbounded memory, the header nobody asked for. Run it, even briefly. |
| "It's a small change, no deployment checklist needed." | Then the checklist is two lines. Small changes with migrations or config are exactly what causes surprise outages. |
| "Rollback is just `git revert`." | Not if the change wrote data in a new shape or ran a migration. Say what reverting actually requires. |

# Edge cases

- **Feature touches a database migration**: the deployment checklist must
  address migration ordering relative to code deploy — read
  `references/deployment-checklists.md` and, if `production-code-review`
  runs on this change, its API-contracts-and-compatibility reference.
- **Change is large enough that "smallest viable" is still substantial**:
  consider whether it should be split into an incremental sequence of
  smaller, independently-shippable changes, and say so.
- **Acceptance criteria turn out to be wrong/incomplete mid-implementation**:
  stop and re-clarify (step 2) rather than implementing against a guess.
- **Rollback plan is non-obvious** (migrations, external side effects):
  read `references/rollback-strategies.md` before finalizing step 15.

# References

See `examples/add-rate-limiting-walkthrough.md` for a full worked example
of this workflow, including a skill handoff to `production-code-review`.
