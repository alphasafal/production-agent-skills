# Severity rubric

Severity = **reachability** (who can trigger it, with what preconditions) x
**impact** (what it yields). The vulnerability class name sets neither.
Every finding gets one line of justification naming both.

## Levels

| Level | Reachability | Impact | Typical action |
|---|---|---|---|
| **Critical** | Anonymous, or any self-registered user, with no special precondition | Full data store read/write, code execution on the server, auth bypass for all accounts, cross-tenant access to all records | Blocks launch |
| **High** | Any authenticated user, or anonymous with a realistic precondition | Cross-tenant read of sensitive records, server file read, account takeover of a targeted user, offline cracking of all passwords after a breach | Blocks launch unless an informed exception is signed off |
| **Medium** | Privileged user (admin of own tenant), or requires an unlikely precondition | Bounded disclosure, defense-in-depth gap that amplifies another bug, debug or error leakage of internals | Fix before or shortly after launch |
| **Low** | Hard to reach, or reachable but low yield | Hardening gaps, unreachable vulnerable dependency function, missing headers with no concrete path to harm | Backlog |

## Adjusting up or down

Raise one level when:
- The data is regulated or high-value (payments, credentials, health, PII).
- The flaw chains with another finding (a leaked signing key plus
  session-based auth gives forgeable sessions).
- The entrypoint is public and unauthenticated.

Lower one level when:
- Reaching it needs an admin role in the caller's own tenant and the impact
  stays inside that tenant.
- A compensating control you verified in code (not assumed) limits the
  yield — e.g. the DB user for that query is read-only on one table.

Never lower because "it's only the dev config" without checking which
config the production entrypoint loads.

## Worked examples: same class, different severity

**SQL injection**
- Search endpoint, any logged-in user, query runs as the app's DB user with
  access to every tenant's rows → **Critical**: any user, full cross-tenant
  read and likely write.
- Internal admin report, admin role only, runs on a read-only replica that
  holds only that tenant's data → **Medium**: privileged reach, bounded yield.

**IDOR**
- `GET /invoices/<id>` returns any tenant's invoice to any logged-in user,
  IDs are sequential → **High**: any user, cross-tenant read of financial
  data, trivially enumerable.
- `GET /avatars/<uuid>` serves public profile pictures by random UUID →
  **Low** or not a finding: the data is intended to be public.

**Path traversal**
- File download handler joins a query parameter onto a base directory and
  serves the result, any logged-in user → **High** (Critical if it can reach
  config with secrets or source): arbitrary server file read.
- Same pattern but the parameter is matched against a fixed allowlist first
  → ruled out, list under "Leads ruled out".

**Weak password hashing**
- Unsalted MD5 → **High**: not directly reachable, but any DB read (including
  via another finding) yields near-instant recovery of most passwords, and
  identical passwords share hashes.
- bcrypt with cost 8 → **Low**: below current recommendations, still salted
  and slow.

**Hardcoded secrets**
- Session signing key committed in the repo and loaded by the production
  config → **High**: anyone with repo access (or a leak of it) can forge
  sessions for any user.
- Placeholder key only in a test fixture, never loaded outside tests → **Low**.

**Debug mode**
- `DEBUG = True` loaded by the production entrypoint on a Werkzeug dev server
  → **Critical**: the interactive debugger allows code execution.
- `DEBUG = True` only honoured by `app.run()` while production runs under
  gunicorn → **Medium**: not active in prod today, one config change away.

**Unsafe deserialization**
- Any logged-in user uploads content parsed with `yaml.load` (no SafeLoader)
  or `pickle.loads` → **Critical**: object construction during parsing can
  run code on the server.

**Vulnerable dependency**
- Advisory affects a function the app calls with user input → rank as the
  underlying class.
- Advisory affects a function the app never calls → **Low** with that reason.

## Status labels

- **CONFIRMED** — entry route, code path and unguarded line are all
  established from the code.
- **LIKELY RISK** — one link depends on something you could not see
  (runtime config, a proxy, an external service). Say which link.
