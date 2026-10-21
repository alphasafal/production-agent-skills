# Answer key: spec-and-plan / Team invitations brief

Fixture: `evaluations/fixtures/spec-and-plan/` (`brief.md`, `app/models.py`,
`app/routes.py`, `app/emails.py`). Grader-only.

The brief has five planted gaps. A correct run surfaces all five in
`SPEC.md` (as open questions, labelled assumptions, or non-goals as
appropriate), writes testable acceptance criteria, and produces a `PLAN.md`
of vertical slices beginning with a walking skeleton. No implementation code.

## 1. Invite expiry is unspecified

**Where:** brief, "What we want": "Invite links shouldn't work forever."

**Why it matters:** expiry decides a column (`expires_at`), the accept-time
check, what the invitee sees on an expired link, and whether resend issues a
new token or extends the old one. Without a number the implementer picks
one silently.

**Expected:** `Q-n` ("How long should invites last? Does resend reset it?")
or `A-n` with a concrete default (7 or 14 days is typical; any number is fine
if labelled), plus an AC for the expired link. Credit runs that also ask
whether revoke and resend invalidate the previous link.

## 2. Existing account vs new user is unclear

**Where:** brief: "get in with as little friction as possible — we don't
want a separate sign-up step". `routes.py` `signup()` requires a password
and rejects existing emails; `User.password_hash` is non-nullable;
`email_verified_at` exists.

**Why it matters:** three different flows: (a) invitee already has an
account and is signed in, (b) has an account but is signed out or signed in
as someone else, (c) has no account. (c) needs either an inline
set-password step on the accept page or a passwordless/magic-link account,
which `password_hash nullable=False` doesn't allow today. It also decides
whether accepting an emailed link may mark `email_verified_at`, and what
happens when the signed-in user's email differs from the invited email.

**Expected:** an open question (preferred, since it changes the data model
and auth) or a labelled assumption with a default, plus ACs for at least
existing-signed-in and new-user paths. Strong runs note the
mismatched-email case and that email matching should be case-insensitive
(signup lowercases; invites must too).

## 3. "Billing admin" role does not exist

**Where:** brief: "Billing admins should also get a heads-up email whenever
someone new joins". `models.py` `Role` has only OWNER, ADMIN, MEMBER,
VIEWER.

**Why it matters:** either a new role (enum change + migration + permission
decisions everywhere `require_role` is used + who can grant it) or it means
the owner, or a notification preference. This is not a detail; it is a
separate design decision hiding in one sentence.

**Expected:** flagged explicitly as not existing in the code, raised as a
`Q-n` ("who is the billing admin — owner? a new role? a setting?"), with the
join notification either assumed to go to the owner (labelled) or parked
until answered. Must NOT silently add a `BILLING_ADMIN` role to the plan
without flagging it.

## 4. Seat limits vs plan tier

**Where:** brief: "Free, Team and Business plans all get invitations."
`models.py`: `PLAN_SEAT_LIMITS` (Free 3, Team 25, Business unlimited),
`Workspace.seats_used()` counts Membership rows.

**Why it matters:** a Free workspace with 2 members can invite 10 people.
Questions: do pending invites reserve seats? What happens when an invite is
accepted after the workspace filled up? Is the inviter blocked, warned, or
shown an upgrade prompt? Does accept fail, and what does the invitee see?
Race: two invites accepted at once for the last seat.

**Expected:** raised as a `Q-n` or labelled `A-n` (e.g. "pending invites
count toward the limit; accept re-checks and fails with an explanatory
page"), with ACs at the limit and one over. Credit noting the concurrent
accept race and the upgrade-prompt product question.

## 5. "Request to join" is a second feature

**Where:** brief, "Also" section: domain-based "Request to join" with admin
approval for enterprise pilots.

**Why it matters:** different actor (the requester, not an admin), different
trigger (signup with matching domain), needs domain verification (otherwise
anyone with an `@acme.com` lookalike or any signup can enumerate
workspaces), an approval queue, and its own notifications. It has no
success metric in the brief. Bundling it roughly doubles the plan.

**Expected:** moved to Non-goals / split into its own brief for product to
scope, with a one-line reason. Acceptable: noting that the invitation data
model could later support it. Fail: tasks for request-to-join in `PLAN.md`.

## Other things a strong run notices (credit, not required)

- `emails.py` sends synchronously through Postmark in the request; inviting
  a pasted list of 30 emails means 30 sequential API calls in one request.
  Risk with a mitigation (background job) or an assumption of a cap.
- `add_member_by_id` in `routes.py` is the current add path; spec should say
  whether it stays (backward compatibility) and whether it bypasses seat
  limits too.
- Duplicate handling: inviting someone already a member, or already
  pending.
- Who can invite as admin: can an admin invite another admin, or only the
  owner? (`require_role(OWNER, ADMIN)` pattern.)
- Invite token must be unguessable and single-use.
- Alembic migration for the new `invitations` table (named in the models
  docstring).

## What good slices look like

A walking skeleton first, then widening. Roughly:

| ID | Slice | Size |
|---|---|---|
| T1 | Walking skeleton: owner/admin invites one email as member from the Members page → invite row + email with tokenized link → existing, signed-in user with that email clicks it → membership created (behind a flag) | M |
| T2 | Pending invites listed on Members page; revoke a pending invite (link stops working) | S |
| T3 | Expiry (per Q/A) + resend (new token or extended expiry per decision) | S |
| T4 | Role picker: admin / member / viewer, with permission check on who may grant what | S |
| T5 | New-user acceptance path (blocked on the existing-vs-new question) | M |
| T6 | Paste multiple emails; dedupe against members and pending invites | S |
| T7 | Seat-limit enforcement at invite and accept time (blocked on seat question) | S |
| T8 | Join notification to billing admin / owner (blocked on role question) | S |
| T9 | Remove flag, metrics events for acceptance rate | S |

Order can vary (e.g. seat limits before multiple emails), but the first build
task must be end to end, each task must cite acceptance criteria, have a
definition of done and size, and tasks blocked on open questions must be
marked. T2/T4/T6 are reasonable parallel candidates after T1.

**Fail patterns:** "T1 add invitations table / T2 invite API / T3 email
templates / T4 Members page UI / T5 tests"; any task called backend,
frontend, database or testing; a plan with code blocks containing function
bodies or a migration file.
