# Worked example: auditing a document-sharing portal

**Prompt:** "We're going through SOC 2 next month. Audit the portal service
for security issues first."

The service is an Express + Postgres app (`src/`) where clients of an
accounting firm upload documents and staff review them. Abridged
`SECURITY_AUDIT.md` output:

---

# Security audit — portal-service @ `4f1c2e9`

## Scope & attack surface

- **Audited:** `src/` (Express app), `package.json` / `package-lock.json`,
  `config/`. Production entrypoint: `node src/server.js` behind nginx
  (`deploy/nginx.conf` read for headers only).
- **Trust boundaries:** anonymous visitors; logged-in **clients** (each
  belongs to one `firm_id` and should see only their own documents);
  **staff** (see all documents in their firm).
- **Authn:** `express-session` with a Postgres store; signing secret from
  `process.env.SESSION_SECRET`. **Authz:** `requireLogin` and
  `requireStaff` middlewares; ownership columns `documents.client_id`,
  `documents.firm_id`.

| Route | Method | Auth | Untrusted inputs |
|---|---|---|---|
| `/login` | POST | none | `email`, `password` |
| `/documents` | GET | client/staff | `sort`, `page` |
| `/documents/:id` | GET | client/staff | `:id` |
| `/documents` | POST | client | multipart file, `title` |
| `/documents/:id/comments` | POST | client/staff | `:id`, `body` |
| `/preview` | GET | client/staff | `url` |
| `/staff/clients` | GET | staff | `q` |

## Findings summary

| ID | Severity | Title | Location | Status |
|---|---|---|---|---|
| F1 | High | Clients can read other clients' documents | `src/routes/documents.js:getDocument` | CONFIRMED |
| F2 | High | Server-side request to user-supplied URL | `src/routes/preview.js:preview` | CONFIRMED |
| F3 | Medium | Stored HTML in comments rendered unescaped | `src/views/document.ejs` | CONFIRMED |
| F4 | Medium | Session cookie missing `Secure`, no login rate limit | `src/app.js` | CONFIRMED |
| F5 | Low | `multer` upload has no size limit | `src/routes/documents.js:upload` | LIKELY RISK |

## Finding details

### F1 — High — Clients can read other clients' documents (IDOR)

- **Location:** `src/routes/documents.js`, `getDocument`.
- **Reachability evidence:** entry is `GET /documents/:id`, guarded only by
  `requireLogin`. The handler calls `Documents.findById(req.params.id)`,
  which runs `SELECT * FROM documents WHERE id = $1` — no `client_id` or
  `firm_id` condition. The sibling `listDocuments` scopes by
  `req.session.clientId`, so the list view is safe and the detail view is
  not. Document IDs are a serial column, so valid IDs are guessable.
- **Impact:** any client can read tax returns and statements belonging to
  any other client of any firm.
- **Severity:** High — any authenticated client, cross-tenant read of
  regulated financial documents.
- **Fix:** change `findById` to `findForViewer(id, viewer)` that adds
  `AND client_id = $2` for clients and `AND firm_id = $2` for staff; return
  404 when no row matches. Apply the same scope in `addComment`, which
  looks up the document the same way.

### F2 — High — Server-side request to user-supplied URL (SSRF)

- **Location:** `src/routes/preview.js`, `preview`.
- **Reachability evidence:** entry is `GET /preview?url=`, any logged-in
  user. `req.query.url` is passed unmodified to `axios.get(url)` and the
  response body is returned to the caller. No scheme, host, or IP
  allowlist is applied anywhere on the path. The service runs on a cloud VM
  (`deploy/README.md`), so internal addresses, including the metadata
  service, are routable from it.
- **Impact:** a user can make the server fetch internal-only endpoints and
  read the responses, including instance credentials.
- **Severity:** High — any authenticated user; yields internal network
  access and likely cloud credentials.
- **Fix:** restrict previews to an allowlist of hosts the product needs; if
  arbitrary hosts are required, resolve the hostname, reject private,
  loopback and link-local ranges, and connect to the resolved IP. Require
  IMDSv2 on the VM as defense in depth.

### F3 — Medium — Stored HTML in comments rendered unescaped

- **Location:** `src/views/document.ejs`, comment loop.
- **Reachability evidence:** entry is `POST /documents/:id/comments`, field
  `body`, stored verbatim by `Comments.create`. The view renders it with
  `<%- c.body %>` (unescaped output) instead of `<%= %>`. Staff open
  documents from many clients, so a client's comment reaches staff
  sessions.
- **Impact:** script runs in the reviewing staff member's browser with
  their session.
- **Severity:** Medium — requires a staff member to open the document; the
  session cookie is `HttpOnly`, which limits but doesn't remove the impact.
  Would be High without `HttpOnly`.
- **Fix:** render with `<%= c.body %>`; if formatting is needed, render
  Markdown server-side and sanitize with an allowlist (DOMPurify). Add a
  `Content-Security-Policy` without `unsafe-inline`.

### F4 — Medium — Session cookie missing `Secure`; no login rate limit

- **Location:** `src/app.js`, `session({...})` and the `/login` route.
- **Reachability evidence:** `cookie: { httpOnly: true }` sets no `secure`
  or `sameSite`. nginx terminates TLS but `deploy/nginx.conf` also listens
  on port 80 without a redirect, so the cookie can be sent in cleartext.
  `/login` has no rate limiting middleware and no lockout.
- **Impact:** session theft on hostile networks; unthrottled password
  guessing.
- **Severity:** Medium — needs network position or many attempts.
- **Fix:** `cookie: { httpOnly: true, secure: true, sameSite: "lax" }`,
  `app.set("trust proxy", 1)`, redirect port 80 to 443 with HSTS, and add
  `express-rate-limit` on `/login` keyed by IP and email.

### F5 — Low — Upload has no size limit (LIKELY RISK)

- **Location:** `src/routes/documents.js`, `multer({ dest })`.
- **Reachability evidence:** no `limits.fileSize`. nginx
  `client_max_body_size` is not set in the config I could see; if a
  default or upstream limit exists, this is mitigated.
- **Fix:** `limits: { fileSize: 20 * 1024 * 1024 }` and an explicit nginx
  limit.

## Leads ruled out

- **`/staff/clients?q=` uses a long concatenated SQL string** — traced:
  the concatenation only joins fixed clause strings; `q` is passed as `$1`
  to `pool.query`. Parameter-bound; not injectable.
- **`sort` on `GET /documents`** — mapped through `SORT_COLUMNS[sort] ??
  "created_at"`; unknown values fall back. Safe.
- **`npm audit`: `semver` ReDoS advisory** — only used by a build tool in
  `devDependencies`; not in the runtime path. Low, upgrade at leisure.
- **Password storage** — `bcrypt.hash(pw, 12)`; salted and slow. Fine.

## Not covered

- nginx and VM hardening beyond the headers and listeners noted above.
- The background OCR worker (`worker/`), out of scope per the requester.
- Dynamic testing of any kind; all findings are from code reading.
- Third-party storage bucket policies (configured outside this repo).
