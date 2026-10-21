# Postmortem template and quality bar

A postmortem exists to make the next incident less likely or less painful. It
is blameless: it assumes everyone acted reasonably on the information they had,
and asks what in the system let a reasonable action cause harm.

## Template

```markdown
# Postmortem: <short title> (<date>, SEV<n>)

Status: draft | reviewed   Incident lead: <name>   Author: <name>

## Summary
Two to four sentences: what broke, for whom, for how long, how it was stopped.

## Impact
- Duration: <onset> to <recovery> UTC (<n> min), from the metric, not the page.
- Requests/users affected: <numbers and how they were calculated>.
- Revenue or business impact: <estimate and assumptions>.
- Data impact: <none / orders to repair / charges to reverse>.

## Timeline (UTC)
| Time | Event |
|---|---|
| HH:MM | First change / onset / alert / ack / decision / mitigation / recovery / resolved |

## Detection
How we found out, how long after onset, and whether the right alert fired.

## Response and mitigation
What was tried, in order, and what worked. Note time-to-mitigate.

## Contributing factors
Several factors, each a property of the system or process, not a person.
- Change factor: what changed.
- Safeguard gaps: why review, tests, canary, or alerts did not stop it.
- Amplifiers: what made the impact larger or longer (retries, missing runbook, unclear ownership).

## What went well

## What went poorly

## Where we got lucky

## Action items
| # | Action | Type | Owner | Priority | Due |
|---|---|---|---|---|---|
| 1 | ... | prevent / detect / mitigate / process | team or role | P0-P2 | date |

## Open questions handed to investigation
What we still do not know, and who is investigating (debugging-investigator run, ticket link).
```

## Quality bar

- **No single culprit.** "Root cause: engineer X changed the timeout" fails.
  "The timeout change was not load-tested and the canary stage was skipped
  for config-only diffs" passes. If a section can be read as blaming someone,
  rewrite it in terms of the system that allowed it.
- **Numbers, not adjectives.** "Many users" fails; "~420 failed checkouts per
  minute for 31 minutes" passes, with the method shown.
- **Timeline from evidence.** Every time comes from a log, metric, or deploy
  record. Mark estimates as estimates.
- **Detection gap stated.** Time from onset to page, and from page to ack.
- **Action items are specific and owned.** Each has one owner (team or role),
  a priority, and a due date. "Be more careful" and "improve monitoring" are
  not action items; "page on checkout 5xx > 1% for 2 min, owner checkout team,
  P1, by Friday" is.
- **Mix of action types.** At least one item that prevents recurrence, one that
  speeds detection, and one that makes mitigation faster or safer.
- **Unknowns are explicit.** If the exact mechanism is not yet confirmed, say
  so and point at the investigation rather than guessing.
- **Red herrings recorded.** Signals that looked related but were ruled out
  go in the timeline with the reason, so the next responder does not chase
  them again.
