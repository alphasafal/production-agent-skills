# Secure fix patterns

Each fix names the standard safe pattern. Avoid blocklists, hand-rolled
escaping, and "sanitize" helpers — they fail open on the case nobody
thought of.

## SQL queries: bind parameters

Python (psycopg2 / sqlite3 / DB-API):

```python
cur.execute(
    "SELECT id, number FROM invoices "
    "WHERE account_id = %s AND customer_name ILIKE %s",
    (account_id, f"%{term}%"),
)
```

The `%` wildcards go into the bound value, not the SQL string. Identifiers
(column or sort names) cannot be bound — map them through a fixed dict:

```python
SORTS = {"date": "issued_on", "total": "total_cents"}
order_col = SORTS.get(request.args.get("sort"), "issued_on")
```

SQLAlchemy: `text("... WHERE id = :id").bindparams(id=x)` or ORM filters.
JavaScript (pg): `pool.query("SELECT ... WHERE id = $1", [id])`.

## Object access: scope every lookup to the caller

Put the ownership condition in the query so a missing check can't be
forgotten in the handler:

```python
def get_invoice(account_id, invoice_id):
    return query(
        "SELECT ... FROM invoices WHERE id = %s AND account_id = %s",
        (invoice_id, account_id), one=True,
    )

invoice = db.get_invoice(g.user["account_id"], invoice_id)
if invoice is None:
    abort(404)  # 404, not 403: don't confirm the ID exists
```

Apply the same scope to child lookups (line items, attachments). For ORMs,
query through the relationship (`current_account.invoices.get(id)`).

## File paths: resolve and contain

Prefer not taking a path at all — store exports in a table keyed by ID and
owner, and serve by ID. If a filename must come from the request:

```python
from pathlib import Path

base = Path(app.config["EXPORTS_DIR"]).resolve()
target = (base / name).resolve()
if not target.is_relative_to(base) or not target.is_file():
    abort(404)
# then also check the file belongs to the caller's account
```

Flask: `send_from_directory(base, name)` performs the containment check.
Node: `path.resolve(base, name)` then `startsWith(base + path.sep)`.

## Passwords: salted, slow hash

```python
from argon2 import PasswordHasher
ph = PasswordHasher()
password_hash = ph.hash(password)
ph.verify(password_hash, candidate)  # raises on mismatch
```

Or `bcrypt.hashpw(pw, bcrypt.gensalt(rounds=12))` /
`werkzeug.security.generate_password_hash(pw)` (scrypt/pbkdf2 by default).
Migration: on next successful login, verify against the old hash, re-hash
with the new scheme, and store it; force reset for accounts that don't log
in within a deadline. Compare hashes with `hmac.compare_digest` if you ever
compare manually.

## YAML and other deserialization

```python
data = yaml.safe_load(upload.read())
```

Then validate shape and types (pydantic / marshmallow / jsonschema) before
use. Never `pickle.loads`, `yaml.load` without `SafeLoader`, or
`jsonpickle.decode` on untrusted bytes. Upgrade PyYAML to a current 6.x
release as well.

## Secrets and config from the environment

```python
import os

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]          # fail fast if missing
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DEBUG = os.environ.get("FLASK_DEBUG") == "1"   # off unless explicitly on
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
```

Load real values from a secrets manager or the deploy environment. Any
secret that was ever committed must be **rotated** — removing it from the
file does not remove it from git history or from anyone's clone. Invalidate
existing sessions after rotating a signing key.

## Error handling and debug

Register a generic error handler that logs the exception server-side and
returns a body with no stack trace. Never run the framework's development
server or interactive debugger in production.

## Dependencies

Pin to patched versions, commit a lockfile, and run `pip-audit` /
`npm audit` in CI so regressions are caught at merge time.
