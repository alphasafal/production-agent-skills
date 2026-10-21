# Answer key: incident-responder workflow eval

Grader only. The fixture is copied into the agent's workspace as
`checkout-oncall/`. Times are UTC on 2026-10-14.

## What actually happened

`checkout-api v2.14.0` deployed at 14:02:06 (`deploys.log`). Its changelog
lowers the payment-client timeout from 5000ms to 1200ms and cuts the HTTP pool
from 64 to 16 connections. Normal provider latency already reaches 1.3-1.9s
(`logs/checkout-app.log` 14:00-14:01, before the deploy), so many authorisations now
time out (`PaymentClientTimeout ... exceeded 1200ms`). Slow calls hold the
smaller pool, so requests queue and fail with `PoolTimeoutError` (waiting
count grows 23 -> 112), producing 503/504s. Retries (`attempt=2/3`) add load.

The exact mechanism is for a follow-up investigation. The incident responder
only needs the correlation to justify a rollback.

## Planted items and expected conclusions

| # | Item | Where | Correct conclusion |
|---|---|---|---|
| 1 | Impact onset ~14:03-14:04 | `metrics/checkout_error_rate.csv`: 0.22-0.38% until 14:03 (0.38%, p99 jumps to 1200ms), 2.11% at 14:04, 18.38% at 14:14 | Onset comes from the per-minute metric, ~14:03, not the 14:04:40 alert. |
| 2 | Correlated change | `deploys.log` 14:02:06 checkout-api v2.14.0; log line 14:02:58 shows new pods start with `timeout_ms=1200 max_connections=16` | The only change on the affected service right before onset. Strong candidate; justifies rollback. |
| 3 | Rollback target | `deploys.log`: v2.13.4 deployed 2026-10-13 16:42, ran ~21h clean | Roll back to v2.13.4. Runbook says no schema migrations in this service; changelog is client config + SDK bump. Rollback is safe. |
| 4 | RED HERRING: DB CPU | `alerts.log` DBCPUHigh 13:41, P3, acked by DBA; note says weekly analytics export, query latency normal. `metrics/db_cpu.csv` steps to ~84% at 13:40 and stays flat through 14:14; connections flat ~180-205 | Started 23 min before onset and did not change at onset. Slow-query WARNs (~210ms) appear both before (14:01) and after the deploy at the same level. Not the cause. Note and move on. |
| 5 | Stale runbook | `ops/runbook.md` last reviewed 2025-11-03; lead "on leave until 2026-01"; "High DB CPU: restart checkout-api pods" | Should not be followed blindly. Restarting pods for DB CPU would not help and would reduce capacity mid-incident. Provider-switch advice requires a config redeploy (not the most reversible lever) and the provider is not shown degraded. Good runs flag the runbook as stale in the postmortem. |
| 6 | Other changes | `deploys.log`: catalog-api (2 days old), search-indexer 09:30, flag `gift_wrap_upsell` 11:58 | All hours before onset on other services or paths; ruled out. Listing them in "Changes considered" is a sign of a good run. |
| 7 | Rollback tool | `ops/rollback.sh v2.13.4 "<reason>"` prints confirmation and appends to `deploys.log`; no network | Running it (or stating the exact command) is the expected mitigation. Script output is not verification. |
| 8 | No post-rollback metrics | Fixture has no data after 14:14 | Agent must say it would verify on the live checkout 5xx rate returning to ~0.3% baseline for a sustained window, or state it cannot observe it here and mark mitigation unverified. Must not declare resolved on script output alone. |

## Impact and severity

- ~2,350-2,520 requests/min; at 18% about 420-445 failed checkouts per minute.
- Duration at time of page: ~11-12 min (14:03 to 14:14) and rising.
- Revenue path (checkout/payments) with >5% failing and a support ticket spike
  (9x baseline, `alerts.log` 14:11) => **SEV1**. SEV2 is acceptable only if
  justified with numbers; anything lower is wrong.
- Rough cumulative failed requests 14:04-14:14: ~3,500 (sum of the errors column).

## Expected INCIDENT_LOG.md shape

- Summary with SEV1, roles (solo is fine if stated), impact numbers, next update time.
- Timestamped entries: ack, impact measurement, severity, first status update,
  changes considered (deploy ruled in; DB CPU, flag, other deploys ruled out
  with reasons), rollback decision with undo, rollback command and output,
  verification plan/status.
- At least one status update with a next-update time. Customer-facing text
  should be plain ("some customers are unable to complete checkout"), with no
  internal names and no speculated cause.

## Expected POSTMORTEM.md shape

- Impact with numbers, onset from the metric, detection lag (~1 min from onset
  to warning alert; P1 page not acked for 5 min per `alerts.log` 14:09).
- Contributing factors, not a culprit: timeout/pool change shipped without
  load test against real provider latency; no canary/progressive rollout
  caught a 2% -> 18% climb; retries amplify pool exhaustion; stale runbook;
  slow ack.
- What went well / poorly / lucky.
- Action items each with owner (team/role), priority, and due date. Examples:
  canary with automatic rollback on 5xx (prevent/mitigate); load-test or
  config guardrail for payment-client timeout below observed provider p99
  (prevent); refresh runbook (process); ack escalation (detect).
- Open questions handed to debugging-investigator: confirm the timeout vs pool
  mechanism and the payments-sdk 3.3.1 bump's role before re-shipping.

## Fail conditions

- Blames DB CPU or restarts pods/DB for CPU as the primary action.
- Edits timeout/pool values or reads SDK code to "fix forward" before rolling back.
- No severity or no numbers before acting.
- Declares resolved from `rollback.sh` output with no reference to the error-rate metric.
- Postmortem names a person as the cause, or action items lack owners.
