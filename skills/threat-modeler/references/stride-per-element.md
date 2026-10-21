# STRIDE per element

STRIDE is a set of questions to ask of each element in the data-flow
diagram. Not every category applies to every element type. Use this table to
pick which questions to ask, then answer each one with a concrete attack
sentence or an explicit "not applicable because ...".

| Element type | S | T | R | I | D | E |
|---|---|---|---|---|---|---|
| External entity (user, third-party service, browser) | yes | | yes | | | |
| Process (API server, worker, function) | yes | yes | yes | yes | yes | yes |
| Data store (DB, bucket, cache, queue) | | yes | yes* | yes | yes | |
| Data flow (a request, a callback, a queue message) | | yes | | yes | yes | |

\* Repudiation applies to a store when it *is* the audit log, or when the
absence of a log is what makes an action deniable.

Trust-boundary crossings deserve every applicable category. Flows that stay
inside one trust zone can usually be covered in a line.

## Questions per category

**Spoofing — can someone act as a principal they are not?**
- Which identity does this element trust, and how is it established (session
  cookie, API key, signed token, IP, "it came from our worker")?
- Can an unauthenticated route reach the same data as an authenticated one?
- Does an inbound callback prove which tenant or provider sent it?

**Tampering — can someone change data or code they shouldn't?**
- Can the client choose fields the server should own (`tenant_id`, `owner_id`,
  `role`, `Content-Type`, file path, price)?
- Can a presigned URL or token be reused to overwrite a different object?
- Can a dependency, build artifact, or uploaded file change what code runs?

**Repudiation — can someone deny doing something, and could you prove otherwise?**
- Is there a record of who viewed, downloaded, shared, deleted, or changed
  permissions — with actor, tenant, object, time, and source IP?
- Can the actor who performs an action also erase its record?
- Would incident response be able to answer "who accessed this document"?

**Information disclosure — can someone read what they shouldn't?**
- Are IDs guessable or enumerable? Are list endpoints filtered by tenant
  server-side, on every query?
- Can a server-side process be made to read something and return it (SSRF,
  path traversal, XXE, verbose errors)?
- Is user content served where it can read cookies or call APIs as the viewer?

**Denial of service — can someone exhaust a resource or someone else's budget?**
- Size, count, rate, and duration limits on every upload, fetch, parse, and
  job. Who pays when they're missing?
- Can one tenant's load starve another (shared queue, shared worker pool)?
- Can a small input expand into a huge cost (decompression bomb, pixel flood,
  fan-out, retry storm)?

**Elevation of privilege — can someone gain capabilities they weren't granted?**
- Can a viewer become an editor, a member become an admin, a user in tenant B
  act in tenant A?
- Does parsing untrusted input run in a process with credentials, network
  access, or a shared filesystem (RCE becomes infrastructure access)?
- Does user content execute in an origin that holds admin sessions?

## Category name vs. attack sentence

An attack sentence has an **actor**, an **action on a specific element**, and
a **result**. If any of the three is missing, it isn't a threat yet.

| Not a threat | A threat |
|---|---|
| "Spoofing of users." | "An anonymous user calls `POST /hooks/billing` with a forged body; the endpoint doesn't verify the provider signature, so the attacker marks any invoice paid." |
| "Information disclosure via IDs." | "An authenticated user in tenant B changes `/api/reports/1042` to `/1041` and receives tenant A's report, because the handler loads by ID without checking `tenant_id`." |
| "Tampering with uploads." | "A user requests a presigned PUT for `avatars/u123.png`, then reuses the signature with a different key that the policy doesn't pin, overwriting another user's object." |
| "DoS." | "A free-tier user submits 500 export jobs; the shared worker pool processes them FIFO, so paying tenants' exports queue for hours." |
| "Elevation of privilege." | "A member sends `role: admin` in `PATCH /api/members/me`; the ORM mass-assigns it." |

## Rating guidance

- **Likelihood**: High if an anonymous or ordinary authenticated user can do
  it with a browser or a script and no special knowledge; Medium if it needs
  a specific precondition (a leaked token, a particular file format, insider
  position); Low if it needs a chain of unlikely conditions.
- **Impact**: High if it crosses tenants, yields credentials or code
  execution, or exposes regulated data; Medium if confined to the attacker's
  own tenant or to availability of one feature; Low if cosmetic or
  self-inflicted.
- Rating = the combination; write the justification in one line. When two
  reviewers would disagree, state the condition that would change it.
