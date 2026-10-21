# Worked example: login failures after a session-store flag change

Scenario: the on-call engineer for an Indian edtech platform's `auth-api` is
paged at 09:12 UTC: "LoginSuccessRate < 90% for 2m (current 71%)". Morning
traffic is peaking as students log in for live classes. Below are the two
artifacts a correct run produces.

---

## INCIDENT_LOG.md

```markdown
# Incident: auth-api login failures — 2026-09-03

## Summary
- Severity: SEV1 (declared 09:15, unchanged)
- Status: RESOLVED 10:02
- Roles: lead/comms/ops: on-call (solo until 09:24), comms handed to support-lead at 09:24
- Impact: login success 71% -> 38% at worst (baseline 98.6%); ~1,900 failed logins/min at peak
- Next update: none (resolved)

## Timeline (UTC)
- 09:12 Paged: LoginSuccessRate 71%. Acked. No one else responding.
- 09:14 Metric read: login success per minute 98.6% until 09:06, 93% at 09:07, 71% at 09:12, falling ~6 pts/min. ~3,100 login attempts/min. Onset from metric: 09:07.
- 09:15 Declared SEV1: login is a core access path, >5% failing and falling, live classes start 09:30. Cadence 15 min.
- 09:16 Status update #1 posted (internal + status page). Next update 09:31.
- 09:17 Changes in last 2h: (a) auth-api v5.2.0 deploy at 07:40; (b) flag `sessions_redis_cluster` 0% -> 50% at 09:05 by platform team; (c) Redis cluster CPU alert since 08:30, flat at ~70%; (d) OTP SMS provider status page: green.
- 09:19 Correlation: (b) lands 2 min before onset on the affected path. (a) ran 85 min clean before onset; ruled out for now. (c) started 37 min before onset and stayed flat; does not explain a step change at 09:07; noted, not chased. (d) green, and failures are on password logins too.
- 09:20 Decision: turn `sessions_redis_cluster` back to 0%. Reversible in one click; off-path (old session store) served 100% until 09:05. Rejected: rollback v5.2.0 (not correlated), scale auth-api (CPU 35%, not saturated). Undo: set flag back to 50%.
- 09:21 Flag set to 0% (flag service audit id fx-20931). Propagation ~60s.
- 09:24 Login success 81%. Support-lead takes comms.
- 09:27 Login success 97.9%.
- 09:31 Status update #2 posted: monitoring.
- 09:46 Login success 98.4-98.8% for 19 min. Support tickets for "can't log in" back to baseline. Update #3.
- 10:02 Resolution criteria met: 35 min at baseline, no related alerts open. Resolved. Update #4.
- 10:05 Root cause handed to debugging-investigator: why do sessions written to the new Redis cluster fail validation? Evidence attached: auth-api error `SessionDecodeError: unknown codec` on 50% of requests from 09:05-09:21.

## Changes considered
| Change | Time vs onset | Verdict |
|---|---|---|
| Flag sessions_redis_cluster 0->50% | -2 min | Ruled in; flag off restored service |
| auth-api v5.2.0 | -87 min | Ruled out: 85 min clean after deploy |
| Redis CPU alert | -37 min, flat | Ruled out: no step change at onset |
| OTP SMS provider | n/a | Ruled out: status green, password logins also failing |

## Status updates
1. 09:16 internal: [SEV1] auth-api — investigating. Login success 71% (baseline 98.6%) since 09:07, falling. Checking recent changes. Next update 09:31.
   09:16 status page: Investigating — Some students are unable to sign in. We are working on it. Next update by 09:31 UTC.
2. 09:31 internal: [SEV1] monitoring. Turned off flag sessions_redis_cluster at 09:21; login success 97.9%. Next update 09:46.
   09:31 status page: Monitoring — A fix has been applied and sign-in is recovering. Next update by 09:46 UTC.
3. 09:46 internal: [SEV1] monitoring. 98.6% for 19 min. Will resolve at 10:01 if it holds.
4. 10:02 status page: Resolved — Sign-in has worked normally since 09:27 UTC. Between 09:07 and 09:27 UTC some students could not sign in. We are sorry for the disruption.
```

---

## POSTMORTEM.md

```markdown
# Postmortem: login failures after session-store flag ramp (2026-09-03, SEV1)

Status: draft   Incident lead: auth on-call   Author: auth on-call

## Summary
Between 09:07 and 09:27 UTC up to 62% of logins failed after the flag
`sessions_redis_cluster` was ramped to 50%. Sessions written to the new cluster
used a codec the validating path did not support. Turning the flag off restored
service within 6 minutes of the decision.

## Impact
- Duration: 20 min of customer impact (09:07-09:27), from login success rate.
- ~27,000 failed login attempts (sum of per-minute attempts x failure rate); an
  estimated 9,000 distinct students, many retrying.
- About 1,100 students joined live classes late (class attendance data).
- No data loss; sessions were recreated on next login.

## Timeline (UTC)
| Time | Event |
|---|---|
| 09:05 | Flag sessions_redis_cluster ramped 0% -> 50% |
| 09:07 | Onset: login success starts falling |
| 09:12 | Page fires (5 min after onset) |
| 09:15 | SEV1 declared |
| 09:21 | Flag set to 0% |
| 09:27 | Login success back at baseline |
| 10:02 | Resolved after 35 min at baseline |

## Detection
The alert needs 2 min below 90%, so it fired 5 min after onset. A rate-of-change
alert would have fired at ~09:08.

## Response and mitigation
Changes were listed and correlated in 3 min; the flag was the only change near
onset. Flag off was chosen over rollback and scaling because it was the most
reversible lever and matched the onset. Time to mitigate: 14 min from onset.

## Contributing factors
- The flag ramp jumped from 0% to 50% with no 1% or 5% stage.
- The new cluster's client used a different default codec; no integration test
  covers sessions written by one store and read by another.
- Flag changes do not show up in the incident channel, so the correlation
  needed a manual lookup.
- Peak traffic (class start) amplified impact.

## What went well
- Onset taken from the metric, not the alert, which made the 2-min gap to the flag change obvious.
- The Redis CPU alert was ruled out quickly instead of chased.
- Updates went out on the 15-min cadence.

## What went poorly
- 5 min from onset to page.
- Solo responder for the first 12 min.

## Where we got lucky
- The ramp was 50%, not 100%.

## Action items
| # | Action | Type | Owner | Priority | Due |
|---|---|---|---|---|---|
| 1 | Require staged ramps (1/5/25/50/100) for flags on auth paths | prevent | platform team | P0 | 2026-09-10 |
| 2 | Integration test: session written by each store is readable by each reader | prevent | auth team | P1 | 2026-09-17 |
| 3 | Rate-of-change alert on login success (>5 pts drop in 1 min) | detect | auth team | P1 | 2026-09-10 |
| 4 | Post flag changes to #deploys alongside deploys | mitigate | platform team | P2 | 2026-09-24 |
| 5 | Auto-page a second responder for SEV1 | process | SRE | P2 | 2026-09-24 |

## Open questions handed to investigation
- Exact mechanism of `SessionDecodeError: unknown codec`; client default vs
  server config. Assigned to auth team via debugging-investigator, ticket AUTH-2214.
```
