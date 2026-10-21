---
name: incident-responder
description: >
  Runs a live incident as an on-call SRE: declare severity from measured
  impact, assign roles, write a timestamped incident log, correlate onset with
  recent changes, mitigate first (rollback, flag off, failover, shed load),
  verify on the alerting metric, post status updates, resolve, and write a
  blameless postmortem. Use when paged or on call, the site or service is down
  in prod, there is an outage, a sev1/sev2, 5xx or 503 errors or a latency or
  error-rate spike hurting customers right now, or for a rollback call, a status page
  update, or a postmortem. Do not use for root-causing a bug with no live
  impact or a flaky test (use debugging-investigator).
license: MIT
compatibility: >
  Needs read access to alerts, metrics, logs and deploy history, and the
  ability to run the team's mitigation tooling (rollback scripts, flag
  toggles). Network access to dashboards or provider status pages helps but
  is optional.
metadata:
  category: sre
  composes_with:
    - debugging-investigator
    - feature-to-production
---

# Purpose

Stop customer impact as fast as possible, with a record good enough that
nobody has to reconstruct it afterwards. During an incident the goal is
mitigation, not understanding. Root cause comes later, from a calm
investigation, once customers are no longer hurting.

# When to use

- You are paged, or asked to "handle" an alert that shows customers affected now.
- A service is down, degraded, or erroring at a rate users notice.
- Someone asks for a rollback decision, a status update, or a postmortem.

# When NOT to use

- A bug with no live customer impact, a flaky test, or root-causing an
  incident after it is mitigated: use `debugging-investigator`.
- Reviewing CI/CD or deploy configuration before it is turned on: that is a
  pre-production review (`deploy-pipeline-reviewer` if installed), not an incident.
- Building a feature or its rollout plan: use `feature-to-production`.

# Required inputs

- The alert or report: which metric fired, its value, and when.
- Access to metrics, logs, and the change history (deploys, config, flags).
- The available mitigation levers and who may pull them.

If any of these are missing, say which and work with what exists. Never stall
mitigation waiting for perfect data.

# Workflow

Start `INCIDENT_LOG.md` at step 1 and append to it at every step, each entry
prefixed with a UTC timestamp. The log is written as you go, not reconstructed.

1. **Acknowledge.** Record the page, the alerting metric and its current value.
   Note whether anyone else is already responding.
2. **Measure impact and declare severity.** Quantify from data, not adjectives:
   error rate and trend, requests or users affected per minute, revenue path
   involved (checkout, login, payments), start time, and duration so far.
   Assign SEV1-SEV4 using `references/severity-and-comms.md`. When between two
   levels, pick the higher one; downgrading later is cheap.
3. **Assign roles and cadence.** Name the incident lead, the comms owner and
   the ops/hands-on owner, even if all three are you. Set the update cadence
   (SEV1: 15 min, SEV2: 30 min) and write the time of the next update in the log.
4. **Post the first status update** (internal, and customer-facing for SEV1/2)
   from the templates in `references/severity-and-comms.md`: what is affected,
   since when, what is being done, and the next update time. "We are
   investigating" is a valid first update.
5. **Find what changed.** List every change in roughly the two hours before
   onset: deploys, config and flag changes, traffic shifts, dependency or
   provider status, scheduled jobs. Find onset from the per-minute metric, not
   from the alert time, which lags. Correlate: the strongest candidate is a
   change that lands just before onset on the affected service. A signal that
   started earlier and stayed flat did not cause a step change later; note it
   and move on.
6. **Choose the most reversible mitigation.** Use
   `references/mitigation-playbook.md`. Rank by reversibility and blast radius:
   rollback of the correlated deploy, flag off, failover, scale out, shed or
   rate-limit load. Act once a change correlates with onset; you do not need
   proof it is the cause. Log the decision, the alternatives rejected, and why.
7. **Mitigate.** Run the lever. Log the exact command, its output, and the time.
   Make one change at a time so you can tell what worked.
8. **Verify on the alerting metric.** Watch the same metric that paged until it
   is back near its pre-incident baseline for a sustained window (at least 10
   minutes for SEV1/2). If you cannot observe it, say so in the log and list
   who or what must confirm it. If it does not recover, return to step 5 with
   the next candidate.
9. **Keep updating.** Post on the cadence until resolved, including "no change"
   updates. Each update states the current metric value.
10. **Resolve.** Declare resolved only when the resolution criteria hold: the
    alerting metric is at baseline for the window, error budgets have stopped
    burning, and no secondary alert is open. Post the resolution update.
11. **Hand off root cause.** Write the open questions and the evidence collected
    so far, and hand them to `debugging-investigator`. Do not root-cause code
    before this step.
12. **Write the postmortem.** `POSTMORTEM.md` from
    `references/postmortem-template.md`: blameless, contributing factors rather
    than a single culprit, and action items with owners and priorities.

**Hard rule:** while customers are impacted and a reversible mitigation is
available, mitigate before you read code to understand why.

# Tool & resource guidance

- To assign severity or write a status update, read `references/severity-and-comms.md`.
- To choose between rollback, flag off, failover, scaling and load shedding,
  or to judge whether a rollback is safe (migrations, data writes), read
  `references/mitigation-playbook.md`.
- To write or review a postmortem, read `references/postmortem-template.md`.

Prefer per-minute metrics over alert timestamps for onset. Treat runbooks as
leads, not truth: check their "last reviewed" date and verify steps against
the current system before running them.

# Output contract

`INCIDENT_LOG.md`, kept live, with these sections:

- **Summary** — severity, status (investigating / mitigating / monitoring /
  resolved), roles, impact numbers, next update time.
- **Timeline** — timestamped UTC entries: observations, decisions with
  rationale, commands run with output, verification readings.
- **Changes considered** — each recent change, its time relative to onset, and
  whether it was ruled in or out and why.
- **Status updates** — every internal and customer-facing update as posted.

`POSTMORTEM.md` with: Summary, Impact (numbers and duration), Timeline,
Detection, Response and mitigation, Contributing factors, What went well, What
went poorly, Where we got lucky, Action items (owner, priority, due date), and
Open questions handed to investigation.

# Quality checks

- [ ] Severity is justified by numbers (rate, volume, duration), not adjectives.
- [ ] Onset time comes from the metric and is compared against each change.
- [ ] Mitigation happened before any code-level root-cause work.
- [ ] Verification uses the metric that alerted, or states why it could not.
- [ ] No gap between status updates exceeds the declared cadence.
- [ ] The postmortem names no individual as a cause, and every action item has
      an owner and a priority.

# Red flags

Stop and correct course if any of these are true:

- You are reading source code or a diff line by line while customers are failing and a rollback is available.
- You are about to run a change that cannot be undone (data migration, deleting a queue, dropping a cache tier) to mitigate.
- The last status update in the log is more than 30 minutes old and the incident is not resolved.
- You named a cause because its alert fired first, without checking whether its onset matches the impact onset.
- You are about to write "resolved" and have not read the alerting metric after the mitigation.
- A sentence in the log or postmortem says a person caused the incident.
- You have made two mitigation changes at once and cannot say which one helped.

# Common rationalizations

Excuses that come up under incident pressure, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "Let me confirm the root cause before rolling back." | Confirmation takes an hour; rollback takes minutes and is reversible. If the rollback does not help, you learned that cheaply. |
| "The fix is a one-line config change, faster than a rollback." | A forward fix is new, untested code in a burning system. Roll back to known-good, then ship the fix through normal review. |
| "No point posting an update, nothing has changed." | Silence reads as nobody working on it. "No change, still mitigating, next update 14:45" is the update. |
| "The DB alert fired first, so it must be the cause." | Order of alerts is not causation. A signal that was flat before and during onset did not cause the step change. |
| "Errors are dropping, we can call it resolved." | Dropping is not baseline. Hold the alerting metric at baseline for the full window before resolving. |
| "It was obviously the engineer who shipped it." | A deploy that can break checkout this easily is a system gap: review, tests, canary. Blame hides those fixes. |

# Edge cases

- **No recent change correlates:** check provider status pages, traffic
  source shifts, certificate and quota expiry, and scheduled jobs; prefer
  capacity levers (scale, shed load) while looking.
- **Rollback is unsafe** (forward-only migration, new data format already
  written): use a flag or failover instead and log why rollback was rejected.
- **You cannot observe the metric** (no dashboard access, offline snapshot):
  log the mitigation as unverified, state what reading would confirm it and
  who must take it, and do not declare resolved.
- **Mitigation does not help:** revert it if it added risk, log the result,
  and move to the next candidate in step 5.
- **Several incidents at once:** keep one log per customer-facing symptom and
  link them; do not merge timelines.

# References

- `references/severity-and-comms.md` — severity matrix, cadence, update templates.
- `references/mitigation-playbook.md` — rollback vs flag vs failover vs scaling, and when each is safe.
- `references/postmortem-template.md` — postmortem structure and quality bar.

See `examples/login-outage-incident.md` for a full worked run.
