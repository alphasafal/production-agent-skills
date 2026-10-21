# Vertical slicing patterns

A vertical slice cuts through every layer it needs (schema, logic, route,
UI, email) to deliver one behavior that can be demoed or tested end to end
and merged on its own. A horizontal task builds one layer for every behavior
and delivers nothing until the last one lands.

## Test for a slice

A task is a vertical slice if all four are true:

1. After it merges, some acceptance criterion passes that didn't before.
2. It can merge without the next task (behind a flag if not ready for users).
3. Its done criteria can be checked by someone who didn't write it.
4. It is S or M sized (3 days or less).

## Anti-example: layer split

For a "comment @mentions" feature:

```
T1 Database: add mentions and notifications tables
T2 Backend: parse mentions, permission check, notify, digest endpoints
T3 Emails: mention and digest templates
T4 Frontend: autocomplete and notification bell
T5 Testing
```

Nothing is demoable until T4. Integration bugs surface in T5. If the sprint
ends after T3, nothing ships. T2 is secretly L.

## Pattern 1: walking skeleton first

The thinnest end-to-end path through every layer, hard-coding everything
else. For mentions: author types `@handle` exactly (no autocomplete) →
comment saved with a mention row → one immediate email to that user with a
link to the comment. No digest, no permission edge cases, no bell. It proves
parsing, storage, email and the deep link connect.

Everything after the skeleton widens it.

## Pattern 2: slice by workflow step

Follow the user's journey and make each step its own slice once the skeleton
exists: mention → see it in the bell → open the comment → mark read → mute
the thread.

## Pattern 3: slice by data variation

Same workflow, different input shapes: one mention → many in one comment;
active user → deactivated user; exact handle → display name with spaces or
different case. Each variation is a slice with its own criteria.

## Pattern 4: slice by rule

Add business rules one at a time on top of a working flow: digest batching,
per-comment mention limits, no self-notification, rate limits. Each rule is
small, testable, and can land in any order once the base flow exists.

## Pattern 5: slice by role or actor

Workspace members first, then guests with per-document access, then the
no-access path. Or: the author's experience, then the mentioned user's, then
the document owner who may want a summary.

## Pattern 6: spike, then slice

When an unknown could change the design (provider limits, token format, a
library that may not do what you need), the first task is a time-boxed spike
with a written question. Its output is a decision recorded in the spec, not
merged code.

## Ordering

1. Spikes for unknowns that could change the data model.
2. Walking skeleton.
3. Slices that retire the next-biggest risk.
4. Slices that carry the most user value.
5. Polish and admin tooling.

Mark `parallel: yes` only when two tasks touch different files, or the shared
part (a migration, an interface) has already merged.

## Splitting an L

- Separate the happy path from the error paths.
- Separate one data variation from the rest.
- Separate the rule from the flow it guards.
- Move the admin or back-office view to its own slice.
- If none of these split it, there is an unknown: add a spike.
