# Worked example: spec and plan for scheduled email reports

**Prompt:** "Here's the ticket for scheduled reports (REPORTS-212). Can you
spec it and break it into tasks? We want to pick it up next sprint."

**Ticket summary:** "Users can schedule any saved dashboard to be emailed as
a PDF daily, weekly or monthly to a list of recipients. Recipients outside
the company should be supported for client reporting. Also add a Slack
destination. Reports should arrive at 8am."

**Code read:** `dashboards/models.py` (`Dashboard`, `SavedFilter`),
`dashboards/views.py` (`render_dashboard`), `exports/pdf.py`
(`render_pdf(dashboard_id, filters)` — synchronous, used by the "Download
PDF" button, ~40 s on large dashboards), `jobs/scheduler.py` (Celery beat,
`hourly_tasks`), `notifications/email.py` (`send_email(to, subject, html,
attachments=None)`), `accounts/models.py` (`Organization.timezone` exists,
`User.timezone` does not).

Output, slightly abridged:

---

## SPEC.md

### Goal

Analysts who share the same dashboard with stakeholders every week can set
it up once and have it arrive as a PDF on a schedule, instead of exporting
and emailing by hand. Ticket metric: reduce manual "Download PDF" exports
per active org by 40% within two months.

### Non-goals

- **Slack destination** — split out. It needs an OAuth app, channel
  picker and a different rendering (image, not PDF). Separate ticket for
  product to scope; the schedule model below leaves room for a
  `destination_type`.
- Editing the PDF layout or adding a cover page.
- Per-recipient filters ("each client sees only their rows").

### Open questions

| ID | Question | Why it matters | Blocks | Owner |
|---|---|---|---|---|
| Q-1 | External recipients: any address, or only domains the org admin allows? | Sending dashboard data to arbitrary addresses is a data-exfiltration path; an allowlist adds an admin setting and a slice. | T5 | Product + security |
| Q-2 | Whose permissions does a scheduled report run with when the creator later loses access to the dashboard? | Decides whether we store creator ID and re-check at send time, or pause the schedule. | T4 | Product |
| Q-3 | "8am" in whose timezone? | `User.timezone` doesn't exist; org timezone does. | nothing if A-1 holds | Product |

### Assumptions

| ID | Assumption | Reason | Reversible? |
|---|---|---|---|
| A-1 | 8am is in `Organization.timezone`. | Only timezone in the model; per-schedule override can come later. | yes |
| A-2 | Max 20 recipients per schedule. | Bounds send volume and abuse; no number in the ticket. | yes |
| A-3 | Monthly means the 1st of the month. | Simplest unambiguous rule. | yes |
| A-4 | A failed render retries 3 times, then emails the creator. | Silent failure is the worst outcome for a scheduled report. | yes |

### Acceptance criteria

AC-1: Create weekly schedule
Given an editor of dashboard D in org O (timezone Europe/Berlin)
When they schedule D weekly on Monday to `ana@o.com`
Then a schedule row exists with `next_run_at` = next Monday 08:00 Berlin, and the dashboard shows "Emailed weekly to 1 recipient".

AC-2: Report delivered
Given a schedule whose `next_run_at` has passed
When the hourly job runs
Then `ana@o.com` receives one email with D's PDF attached, rendered with D's saved filters, and `next_run_at` advances one week.

AC-3: Viewer cannot schedule
Given a viewer of D
When they POST a schedule for D
Then the response is 403 and no schedule row is created.

AC-4: Recipient limit (A-2)
Given a schedule form with 21 addresses
When it is submitted
Then it is rejected with "Up to 20 recipients" and nothing is saved.

AC-5: Render failure (A-4)
Given the PDF render fails 3 times for a due schedule
When the third attempt fails
Then the creator receives a "Your scheduled report failed" email and the schedule shows a failed badge.

AC-6: Unsubscribe
Given `ana@o.com` received a scheduled report
When she clicks "Unsubscribe" in the email
Then she is removed from that schedule's recipients without signing in, and receives no further emails from it.

### Technical approach

**Data model** — new `ReportSchedule` in `dashboards/models.py`:
`id`, `dashboard_id` (FK), `created_by_id` (FK users), `frequency`
(enum daily/weekly/monthly), `weekday` (nullable), `recipients` (array of
email, max 20), `next_run_at` (timestamptz, indexed), `last_status`,
`last_error`, `destination_type` (enum, only `email` now).
`ReportUnsubscribe` token per recipient (random 128-bit, unique).

**Migrations** — one additive Alembic migration; no backfill. Rollback is
dropping the two tables.

**Interfaces** — `POST/GET/DELETE /api/dashboards/<id>/schedules` in
`dashboards/views.py`; `GET /reports/unsubscribe/<token>` (no auth). Hourly
Celery task `send_due_reports` in `jobs/scheduler.py` picks rows with
`next_run_at <= now()` using `SELECT … FOR UPDATE SKIP LOCKED`.

**Rendering** — reuse `exports/pdf.render_pdf` inside the worker, not the
web request.

**Backward compatibility** — "Download PDF" unchanged. No existing rows
touched.

### Risks and spikes

| Risk | Likelihood | Impact | Spike / mitigation |
|---|---|---|---|
| `render_pdf` uses request context (session user, `g.org`) and fails outside a request. | High | Blocks AC-2 | S0: call it from a Celery task for 3 real dashboards; record what context it needs. |
| Many orgs at 08:00 Berlin cause a render spike. | Med | Late reports | Spread with per-schedule jitter up to 15 min; measure in S0. |
| Emails with PDFs land in spam. | Med | Silent failure | Send from existing verified domain; check one in a seed inbox during T2. |

---

## PLAN.md

Sizes: S ≤ 1 day, M 2-3 days.

### Slices

| ID | Slice | ACs | Depends on | Size | Parallel |
|---|---|---|---|---|---|
| S0 | Spike: render a dashboard PDF from a Celery worker | — | — | S | yes, with T1 |
| T1 | Walking skeleton: create a weekly schedule for one recipient and see it on the dashboard (flag `scheduled_reports`) | AC-1 | — | M | yes, with S0 |
| T2 | Due schedules send the PDF email and advance `next_run_at` | AC-2 | T1, S0 | M | no |
| T3 | Daily and monthly frequencies, multiple recipients, 20-recipient limit | AC-4 | T2 | S | yes, with T4 |
| T4 | Permissions: viewers can't schedule; re-check creator access at send time | AC-3 | T1; Q-2 | S | yes, with T3 |
| T5 | Unsubscribe link and external-recipient rule | AC-6 | T2; Q-1 | M | yes, with T6 |
| T6 | Failure retries and creator notification | AC-5 | T2 | S | yes, with T5 |
| T7 | Remove flag; docs and changelog | all | T3-T6 | S | no |

### Task detail

**S0 Spike** — Question: what does `render_pdf` need outside a request, and
how long does the largest customer dashboard take? Output: a note in
SPEC.md Risks; no merged code. Done when the answer is written and T2's
approach is updated.

**T1 Walking skeleton** — `ReportSchedule` model and migration (weekly
only); `POST /api/dashboards/<id>/schedules`; schedule form in the dashboard
share menu; status line on the dashboard. Done when AC-1 passes in an
integration test, the flag hides it from users, and it is merged.

**T2 Send due reports** — `send_due_reports` task in `jobs/scheduler.py`
using the S0 approach; email via `notifications/email.send_email` with
attachment. Done when AC-2 passes against a test mailbox and one real email
has been checked for spam placement.

*(T3-T7 follow the same shape.)*

### Blocked on

| Task | Waiting for | Default if no answer by Wednesday |
|---|---|---|
| T4 | Q-2 | Pause the schedule and email the creator when they lose access. |
| T5 | Q-1 | Allow only the org's verified domains; external addresses rejected. |

**Note to the requester:** T1, S0 and T2 are unblocked and can start now.
Q-1 changes who we send company data to, so please confirm before T5.
Slack was moved out of this plan; it needs its own scoping.
