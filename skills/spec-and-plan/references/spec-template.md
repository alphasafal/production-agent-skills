# SPEC.md and PLAN.md skeletons

Copy these, fill every section, and delete the guidance lines. An empty
section must say why it is empty ("No schema changes: reuses `exports`").

## SPEC.md

```markdown
# Spec: <feature name>

Source: <link or path to the brief> · Author: <name> · Status: draft / awaiting answers / approved

## Goal
<One paragraph: which user gets which outcome, and the metric the brief
names. Restate it in your words so misunderstandings show.>

## Non-goals
- <Excluded by the brief>
- <Cut by this spec, with reason>
- <Split out as separate scope: name, why it's separate, who should scope it>

## Open questions
| ID | Question | Why it matters | Blocks | Owner |
|---|---|---|---|---|
| Q-1 | ... | <what changes in the design depending on the answer> | <task IDs or "nothing yet"> | <role> |

## Assumptions
| ID | Assumption | Reason | Reversible? |
|---|---|---|---|
| A-1 | ... | ... | yes / costly |

## Acceptance criteria
AC-1: <name>
Given ...
When ...
Then ...

## Technical approach
### Data model
<New tables/columns/enums with types and constraints. Field lists only.>
### Migrations and backfill
<Migration steps, ordering with deploys, backfill, rollback.>
### Interfaces
<Routes / endpoints / function signatures / events, with request and
response shape. Signatures only.>
### Where changes live
| Change | File / module |
|---|---|
### Backward compatibility
<What existing rows, routes, links, and clients keep doing.>

## Risks and spikes
| Risk | Likelihood | Impact | Spike / mitigation |
|---|---|---|---|
```

## PLAN.md

```markdown
# Plan: <feature name>

Spec: SPEC.md · Sizes: S ≤ 1 day, M 2-3 days (no L)

## Slices
| ID | Slice | ACs | Depends on | Size | Parallel |
|---|---|---|---|---|---|
| S0 | Spike: ... | — | — | S | yes, with ... |
| T1 | Walking skeleton: ... | AC-1 | — | M | no |

## Task detail
### T1 Walking skeleton: <title>
- Changes: <files and what changes in each>
- Flag: <flag name, if user-visible before complete>
- Done when: <ACs passing, tests added, demo path, reviewed and merged>

## Blocked on
| Task | Waiting for | Default if no answer by <date> |
|---|---|---|
```
