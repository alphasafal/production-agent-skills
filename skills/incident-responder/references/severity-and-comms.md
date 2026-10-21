# Severity and communications

## Severity matrix

Pick the highest row any measured impact matches. Adjust thresholds to the
team's SLOs if they exist; these are defaults.

| Sev | Customer impact | Typical numbers | Cadence | Customer-facing update |
|---|---|---|---|---|
| SEV1 | Core revenue or access path broken for many users: checkout, payments, login, data loss or exposure | >5% of requests failing on a revenue path, or full outage of any tier, or any confirmed data loss/leak | 15 min | Yes, within 15 min of declaring |
| SEV2 | Core path degraded, or a secondary path broken | 1-5% failing on a core path, p99 latency >3x SLO, or a major feature fully down | 30 min | Yes, if users can see it |
| SEV3 | Minor feature degraded, workaround exists | <1% failing, single region/tenant, internal tools down | 60 min or on change | Usually no |
| SEV4 | No user impact yet; risk of it (disk filling, cert expiring in days) | — | On change | No |

Rules:

- Measure before declaring: error rate and its trend, request volume, users or
  orders affected per minute, start time, duration so far. Write the numbers
  in the log next to the severity.
- Trend matters. 4% and climbing fast is a SEV1 in ten minutes; declare it now.
- Security exposure or data loss is SEV1 regardless of volume.
- Re-evaluate severity at every update. Upgrade freely, downgrade only after
  the metric has held at the new level for one cadence interval.

## Rough impact arithmetic

- Failed requests per minute = requests/min x error rate.
- Revenue at risk per minute = failed checkouts/min x average order value
  (state the AOV you assumed). Note that some users retry; this is an upper
  bound on lost orders, a lower bound on frustrated users.
- Duration counts from metric onset, not from the page.

## Roles

| Role | Does | Does not |
|---|---|---|
| Incident lead | Owns decisions, severity, when to resolve | Type commands while also deciding |
| Comms | Posts updates on cadence, fields questions from support and leadership | Speculate about cause in public |
| Ops | Runs mitigations, reports output | Make changes the lead has not agreed |

Solo responder: hold all three, and write "lead/comms/ops: <you>" in the log.
Ask for help as soon as a second pair of hands is available; hand off comms first.

## Internal update template

```
[SEV<n>] <service> — <status: investigating | mitigating | monitoring | resolved>
Impact: <metric> at <value> (baseline <value>), since <HH:MM UTC>. <who/what is affected>.
Current action: <what is being done right now>.
Leading hypothesis: <change or factor that correlates, and confidence>.
Next update: <HH:MM UTC> or sooner on change.
Lead: <name>  Comms: <name>
```

## Customer-facing template

Plain language. No internal names, no speculation about cause, no blame of
vendors, no promises of exact fix times.

```
Investigating — <HH:MM UTC>
Some customers are unable to <complete checkout / sign in / ...>. We are
aware and actively working on it. Next update by <HH:MM UTC>.

Identified — <HH:MM UTC>
We have identified the issue affecting <capability> and are applying a fix.
Next update by <HH:MM UTC>.

Monitoring — <HH:MM UTC>
A fix has been applied and <capability> is recovering. We are monitoring
closely. Next update by <HH:MM UTC>.

Resolved — <HH:MM UTC>
<Capability> has been working normally since <HH:MM UTC>. Between <start> and
<end> UTC, some customers <what they experienced>. <If relevant: orders that
failed were not charged / any duplicate charges will be reversed.> We are
sorry for the disruption.
```

## Resolution criteria

All must hold before posting "Resolved":

1. The alerting metric is within normal range of its pre-incident baseline.
2. It has held there for the window: 10 min for SEV2, 15-30 min for SEV1.
3. No related alert is still firing, and support contact rate is falling.
4. Any data repair (failed orders, stuck payments) is either done or tracked
   as a named follow-up with an owner.
