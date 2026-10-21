# Mitigation playbook

Mitigation buys time. It does not need to be the fix, only the fastest safe
way to stop customer impact. Choose by reversibility first, speed second,
blast radius third.

## Levers, most to least preferred

| Lever | Use when | Safe when | Not safe when |
|---|---|---|---|
| Roll back the deploy | Onset follows a deploy of the affected service within minutes | Previous version ran recently in prod; no forward-only migration; data written by the new version is readable by the old one | New version ran a destructive or forward-only migration; new data format already written that the old code cannot parse; rollback target is itself old enough to have known problems |
| Turn a feature flag off | Onset follows a flag change, or the new code path is behind a flag | Flag-off path is the long-running default | Flag has been on long enough that the off-path is stale or untested |
| Revert a config change | Onset follows a config or secret change | Previous value is known and recorded | The old value is gone (rotated secret, deleted resource) |
| Fail over (region, replica, provider) | A dependency or one region is unhealthy and an alternative is warm | Failover has been exercised recently; capacity on the other side is known | Failover is untested, or would split-brain a primary database |
| Scale out | Saturation: CPU, connections, queue depth rising with load | Bottleneck is the scaled tier, not something behind it | Bottleneck is a downstream (DB, provider): scaling sends it more load |
| Shed or rate-limit load | Overload you cannot add capacity for fast enough | You can prioritise (keep checkout, drop recommendations) | Shedding the core path is the incident itself |
| Restart | Leaked state (memory, stuck threads, poisoned cache) | Restart is rolling and capacity remains | Every instance would restart into the same bad state |

## Decision rules

- **Correlation is enough to act.** If a reversible change lands just before
  onset on the affected service, undo it. You are not claiming it is the root
  cause; you are running the cheapest experiment that may end the impact.
- **Roll back rather than fix forward.** A hot fix is new code shipped under
  stress without full review. Fix forward only when rollback is unsafe (see the
  table) and no flag exists, and then keep the change minimal and reviewed by a
  second person if anyone is available.
- **One change at a time.** Apply, wait for the metric to respond (a few
  minutes for a rollout to finish), read it, then decide the next step.
- **Write down the undo before you run it.** For every mitigation, record how
  to reverse it. If you cannot write that line, the action is not reversible.
- **Never mitigate with something irreversible.** Deleting data, purging a
  queue with unprocessed work, dropping a table, or force-pushing over history
  can turn an outage into data loss.
- **Check the runbook's age.** Runbook steps that reference people, config
  keys, or providers can be stale. Verify a step matches the current system
  before running it, and log any step you found to be wrong.

## Rollback safety checklist

Before running a rollback, confirm and log:

1. Target version: the version that was serving just before onset (from
   deploy history, not memory).
2. Migrations: did the bad version run any? Were they additive (safe) or
   destructive/forward-only (unsafe)?
3. Data compatibility: has the new version written anything the old one cannot
   read (new enum values, new serialization, renamed fields)?
4. Shared dependencies: did the deploy also bump a library or a contract other
   services now rely on?
5. Rollout: rolling with capacity kept, or all at once?

## Verifying mitigation

- Watch the metric that paged, not a proxy. If 5xx rate paged, 5xx rate must
  return to baseline; "pods healthy" is not evidence.
- Also check the user-level signal: successful orders per minute, login
  success rate, support ticket rate.
- If the metric does not move within a few minutes of the rollout finishing,
  the change was probably not the trigger. Log that, consider reverting the
  mitigation if it added risk, and go to the next candidate.
- If you cannot see the metric, say so plainly in the log and in the update,
  and mark status "mitigation applied, unverified".
