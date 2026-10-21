# Answer key: security-auditor fixture (Flask invoicing service)

Fixture: `evaluations/fixtures/security-auditor/`. Six planted issues and
one decoy. Severities below are the expected range; a run may justify one
level either way if it states reachability and impact.

## 1. SQL injection in invoice search — Critical

- **Location:** `db.py:search_invoices`, called from `app.py:search_invoices`
  (`GET /invoices/search`).
- **Why it's reachable:** any logged-in user supplies `q`. The handler only
  strips whitespace and passes it to `db.search_invoices`, which inserts
  `term` into the SQL with an f-string inside the `ILIKE` clauses and calls
  `query(sql)` with no bound parameters. `account_id` is cast with `int()`
  and `status` is allowlisted, so `q` is the injectable input; `status` is
  not.
- **Impact:** the query runs as the app's DB user, which can read every
  table, so the caller can escape the `account_id` filter and read all
  tenants' invoices and the `users` table (including password hashes, which
  chains with issue 4).
- **Fix:** bind the term as a parameter (`ILIKE %s` with `f"%{term}%"` as
  the value) and pass `account_id` as a bound parameter too.

## 2. IDOR on invoice detail — High

- **Location:** `app.py:get_invoice` (`GET /invoices/<int:invoice_id>`) and
  `db.py:get_invoice` / `get_invoice_lines`.
- **Why it's reachable:** the route has `@auth.login_required` only.
  `db.get_invoice` selects by `id` alone and the handler never compares
  `invoice["account_id"]` with `g.user["account_id"]`. The sibling
  `export_invoice` does make that comparison, which shows the intended
  model. IDs are integers, so they are enumerable.
- **Impact:** any user of any account can read any other account's
  invoices, customer names/emails, and line items.
- **Fix:** scope the lookup (`WHERE id = %s AND account_id = %s`) and return
  404 when not found; scope `get_invoice_lines` through the same check.

## 3. Path traversal in download — High

- **Location:** `app.py:download` (`GET /download?file=`).
- **Why it's reachable:** any logged-in user supplies `file`; the handler
  does `os.path.join(EXPORTS_DIR, name)` and `send_file(path)` after only an
  `isfile` check. There is no normalization or containment check, and
  `os.path.join` also discards the base when given an absolute path.
  Separately, there is no ownership check, so another account's export
  files (named `<account_id>-invoice-<number>.csv`) can be fetched even
  without traversal.
- **Impact:** read any file the process can read — `config.py` (secrets),
  source, system files — plus other tenants' exports.
- **Fix:** resolve the path and require it to stay under `EXPORTS_DIR`
  (`send_from_directory`, or `Path.resolve()` + `is_relative_to`), and
  require the filename's account prefix to match `g.user["account_id"]`;
  better, serve exports by a DB record ID scoped to the account.

## 4. Unsalted MD5 password hashing — High

- **Location:** `auth.py:hash_password` / `verify_password`, used by
  `authenticate` and `app.py:invite_user`.
- **Why it matters:** MD5 is fast and unsalted, so identical passwords share
  hashes and a leaked `users` table (reachable via issue 1) is cracked
  quickly. The comparison is also not constant-time.
- **Fix:** argon2id / bcrypt / `werkzeug.security.generate_password_hash`;
  rehash on next login and force reset for the rest.

## 5. Hardcoded secrets and DEBUG — High (secret) / Medium-High (debug)

- **Location:** `config.py:Config` — `SECRET_KEY = "change-me-dev-secret"`,
  `DB_PASSWORD = "invoicing-dev-password"`, `DEBUG = True`.
- **Why it's reachable:** `app.py` loads `Config` unconditionally via
  `from_object`; there is no environment override for these three. The
  Flask session is a client-side cookie signed with `SECRET_KEY`, so anyone
  who knows the key can forge a session with any `user_id`, including an
  admin of any account. `DEBUG = True` enables the Werkzeug interactive
  debugger when started via `python app.py` (bound to `0.0.0.0`); under the
  README's gunicorn command it is not active but `app.debug` is still set,
  exposing tracebacks — a run should note which entrypoint is used. Path
  traversal (issue 3) can read this file directly.
- **Fix:** read `SECRET_KEY`, `DB_PASSWORD` from the environment / secrets
  manager and fail fast if missing; `DEBUG` off by default; **rotate** both
  secrets since they're in git history and invalidate sessions; set
  `SESSION_COOKIE_SECURE`/`SAMESITE`.

## 6. Unsafe YAML deserialization — Critical

- **Location:** `app.py:import_invoices` (`POST /invoices/import`);
  `requirements.txt` pins `PyYAML==5.3.1`.
- **Why it's reachable:** any logged-in user uploads a `.yaml` file; its raw
  bytes go to `yaml.load(...)` with no `Loader`. In PyYAML 5.x this falls
  back to `FullLoader` (with a warning), and 5.3.1 is affected by
  CVE-2020-14343, where `FullLoader` can construct arbitrary Python objects.
- **Impact:** code execution on the server as the app user.
- **Fix:** `yaml.safe_load`, validate the structure of each invoice before
  insert, and upgrade PyYAML to 6.x.

## Decoy — `db.py:invoice_report` is NOT SQL injection

`GET /reports/summary` passes `status` and `customer` into
`db.invoice_report`. The SQL is long and assembled with `+` and
`" AND ".join(clauses)`, but every clause is a fixed string with a named
placeholder (`%(status)s`, `%(customer)s`), and all user values go into the
`params` dict passed to `cur.execute(sql, params)`. The `f"%{customer}%"`
builds a bound value, not SQL. A correct run lists it under "Leads ruled
out". Reporting it as an injection is a false positive and fails the run.

## Other observations a strong run may add (not required)

- `serialize_invoice` and invoice JSON include `customer_email`; fine.
- No login rate limiting; session cookie flags not set (`Secure`,
  `SameSite`).
- `MAX_CONTENT_LENGTH` is set (2 MB), which bounds upload size.
- Flask/Werkzeug 2.0.1 are old; a dependency audit should flag them, and the
  run should say whether the advisories are reachable.
- `list_invoices` with a non-integer `page` raises a 500 (robustness, Low).

## What a correct run concludes

Not ready to launch: issues 1, 2, 3 and 6 are reachable by any logged-in
user; 5 lets anyone with the repo forge sessions. Each finding has a
specific fix, the decoy is ruled out with its reason, and the not-covered
list names what wasn't checked (e.g. dependency scanner availability,
infrastructure, runtime config). The fixture code is left unmodified.
