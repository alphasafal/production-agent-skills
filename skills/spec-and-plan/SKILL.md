---
name: spec-and-plan
description: >
  Turns a scoped requirement into an engineering spec and task plan before
  code is written: goals, open questions and labelled assumptions, testable
  acceptance criteria, technical approach, risks and spikes, then ordered
  vertical-slice tasks with dependencies, done criteria and sizes. Use when
  handed an approved ticket, brief or epic and asked to write a tech spec, break it
  down into tasks or tickets, plan the work, estimate it, or get it ready so we
  can start Monday, including rushed just-split-it-up or skip-the-spec
  requests. Do not use for deciding what to build or writing the PRD (use
  product-manager), writing the code (use feature-to-production), or
  reviewing an architecture (use system-design-reviewer).
license: MIT
compatibility: Read access to the brief and the repository it changes. No shell or network access required.
metadata:
  category: engineering
  composes_with:
    - product-manager
    - feature-to-production
    - system-design-reviewer
---

# Purpose

Turn a scoped requirement into a spec a reviewer can disagree with and a plan
a team can start on, before any code exists. Every ambiguity becomes a
visible question or a labelled assumption, every requirement becomes a test,
and every task delivers something that works end to end and can merge alone.

# When to use

- A ticket, PRD, feature brief, or epic exists and someone asks for a tech
  spec, an implementation plan, a task breakdown, or estimates.
- "Break this into tickets", "plan this out so we can start", "what are the
  tasks", "how would we build this" — before implementation begins.
- As the planning stage between `product-manager` (what to build) and
  `feature-to-production` (building it), for anything bigger than a day.

# When NOT to use

- The idea itself is still vague or the question is whether to build it —
  use `product-manager` to scope it and write the PRD first.
- The plan already exists and the ask is to write and ship the code — use
  `feature-to-production`.
- Someone else's architecture doc needs review for scale, consistency or
  cost — use `system-design-reviewer`.
- A conceptual question ("what is a story point?") — answer it directly.
- A change small enough to do in under an hour: say so and skip the plan.

# Required inputs

- The brief: ticket, PRD, or feature description, including any stated
  metrics, out-of-scope list, and design mocks.
- Read access to the code it changes: data model, routes or handlers,
  background jobs, email or notification code, migrations folder.
- Known constraints if any: deadline, team size, release process, flags.

If there is no code to read, say the technical approach is unanchored and
name the files you would expect to touch as assumptions.

# Workflow

1. **Read the brief twice.** First pass for intent; second pass marking every
   noun (entity, role, plan, state) and every verb (create, expire, notify).
   Each one must map to something in the code or become a question.
2. **Read the code it touches.** Open the models, routes, email/notification
   module, auth/permission checks, and migration tooling. Note the exact
   files, classes and functions that will change. Check every entity, role
   and enum the brief names against what actually exists.
3. **Restate goal and non-goals.** One paragraph on the user outcome and the
   metric. Non-goals list what the brief excludes plus anything you are
   cutting; a second feature hiding in the brief ("also", "while we're in
   here") is split out here with a reason.
4. **List ambiguities.** For each gap write either an **open question**
   (design changes depending on the answer) or an **assumption** labelled
   `A-n` with the chosen default and why. Never pick silently. Look hardest
   at: lifetimes and expiry, existing vs new users, limits and quotas,
   permissions, duplicates and retries, and anything named in the brief but
   absent from the code.
5. **Write acceptance criteria.** Given/when/then, one behavior each, with
   concrete values ("after 7 days the link returns the expired page"). Cover
   the happy path, each permission boundary, each limit, and each failure
   the user can see. If a criterion can't become a test, rewrite it.
6. **Describe the technical approach.** Data model and schema changes,
   migrations and backfill, API/route changes, email/job changes, and where
   each lives (file and function). State backward compatibility: what
   existing callers, rows and links keep working.
7. **List risks and unknowns.** For each: what could go wrong, how likely,
   and the spike that retires it (a time-boxed experiment with a question it
   answers). Riskiest unknowns get spikes scheduled first.
8. **Slice vertically.** Start with a walking skeleton: the thinnest path
   that works end to end through every layer. Then add slices by workflow
   step, data variation, rule, or role. Each slice is user-visible or
   testable end to end and mergeable alone (behind a flag if needed). No
   task is a layer ("backend", "DB", "UI").
9. **Order and annotate.** Order by dependency, then risk (riskiest first).
   Each task gets: ID, the acceptance criteria it satisfies, depends-on,
   definition of done, size (S ≤ 1 day, M 2-3 days, L > 3 days; split any L),
   and `parallel: yes/no` with what it can run alongside.
10. **Stop on blocking questions.** If any open question changes the data
    model, permissions, or slice order, present the spec and ask before
    finalising the plan. Mark tasks that depend on an unanswered question.

**Hard rule:** no implementation code during planning. Schema field lists,
route signatures and pseudocode-level interfaces are fine; working functions
are not.

# Tool & resource guidance

- For step 5, if criteria keep coming out vague or untestable, read
  `references/acceptance-criteria.md` for the given/when/then rules and
  before/after rewrites.
- For step 8, if the work keeps splitting into layers or one slice is still
  L-sized, read `references/vertical-slicing.md` for walking skeleton,
  slice-by-workflow-step, data-variation, rule and role patterns.
- When writing the files, use `references/spec-template.md` for the exact
  section skeletons of `SPEC.md` and `PLAN.md`.
- Use search (grep, file listing) to confirm every enum, role, table and
  route the brief mentions exists before relying on it.

# Output contract

Produce two files.

`SPEC.md`, sections in order:
- **Goal** — outcome and metric, one paragraph.
- **Non-goals** — including split-out scope and why.
- **Open questions** — numbered `Q-n`, each with who answers and what it blocks.
- **Assumptions** — numbered `A-n`, each with the default and its reason.
- **Acceptance criteria** — `AC-n`, given/when/then.
- **Technical approach** — data model, migrations, interfaces, file locations,
  backward compatibility.
- **Risks and spikes** — risk, likelihood, spike that retires it.

`PLAN.md`, sections in order:
- **Slices** — ordered table: ID, title, ACs covered, depends on, size,
  parallel.
- **Task detail** — per task: what changes where, definition of done.
- **Blocked on** — tasks waiting for a `Q-n` answer.

# Quality checks

- [ ] Every entity, role, and limit in the brief maps to code or to a `Q-n`/`A-n`.
- [ ] Every acceptance criterion names concrete inputs and an observable result.
- [ ] Every AC is covered by at least one task, and every task cites an AC.
- [ ] The first build task is a walking skeleton that works end to end.
- [ ] No task is named after a layer; each one can merge on its own.
- [ ] Every task has a size and a definition of done; no L remains unsplit.
- [ ] Scope that is really a second feature is in Non-goals, not in the plan.
- [ ] No implementation code appears in either file.

# Red flags

Stop and correct course if any of these are true:

- You are writing a function body, a migration file, or a test file.
- A task title is "backend", "database layer", "API", "frontend", or "wire it up".
- An acceptance criterion says "works well", "is fast", "handles errors", or "is intuitive".
- The brief names a role, plan, state or limit you have not looked up in the code.
- You resolved an ambiguity in the brief and there is no `Q-n` or `A-n` recording it.
- No task in the plan could be merged and demoed without a later one.
- The plan contains an "also" item from the brief that has no user, metric, or acceptance criteria of its own.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "The brief is clear enough." | Clear to the author. Expiry, existing accounts, limits and permissions are almost never specified; the first engineer to hit them picks silently and the reviewer finds out in QA. |
| "We'll figure out edge cases during implementation." | Edge cases are where the data model changes. Found mid-sprint, they cost a migration and a re-plan; found now, they cost a question. |
| "Splitting by layer is more natural." | Layer tasks can't be demoed or merged alone, hide integration risk until the end, and leave nothing shippable if the sprint runs out. |
| "Estimates are pointless." | Sizes exist to find the task that is secretly three tasks. An L you can't split is a risk you haven't named. |
| "They said start Monday, so skip the questions." | Asking now costs an hour. Building the wrong expiry or seat rule costs the week. Ship the spec with questions and the unblocked slices. |
| "I'll include the extra request since it's related." | Related is not the same scope. A second feature doubles the plan and the risk; split it and let product scope it. |
| "Showing the code is clearer than describing it." | Code in a plan gets copied unreviewed. Field lists and signatures are reviewable; function bodies are a premature PR. |

# Edge cases

- **Brief is really still an idea** (no user, no metric, no scope): stop and
  route to `product-manager` rather than inventing requirements.
- **No codebase yet**: write the approach against stated assumptions and make
  "walking skeleton plus project setup" the first slice.
- **Open question nobody can answer this week**: choose the reversible
  default as an assumption, flag it, and order slices so it lands late.
- **Hard deadline**: keep all slices, mark which form the minimum shippable
  set, and say what is cut if time runs out.
- **Change spans teams or services**: give each slice an owner and name the
  contract between them as its own early task.

# References

- `references/acceptance-criteria.md` — given/when/then rules, coverage
  checklist, untestable-to-testable rewrites.
- `references/vertical-slicing.md` — walking skeleton and slicing patterns
  with layer-split anti-examples.
- `references/spec-template.md` — `SPEC.md` and `PLAN.md` skeletons.
- `examples/scheduled-reports-plan.md` — a full worked spec and plan for a
  scheduled email reports feature.
