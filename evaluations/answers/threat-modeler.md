# Answer key: threat-modeler / Shared Documents design

Fixture: `evaluations/fixtures/threat-modeler/design.md`. Grader-only.

The design has six planted weaknesses. A correct run finds all six, writes
each as a concrete attack against the named component, rates them with
spread (not all the same), and maps each to a specific mitigation and a
testable security requirement. Items 1-3 are required behaviors; 4-6 are
expected in a strong run and their absence should be noted in grading.

Expected trust boundaries in the data-flow diagram, at minimum: internet ↔
app (`app.teamboard.io`), anonymous ↔ app (`/share/*`), app ↔ arbitrary
external URL (import), app ↔ S3 (presigned, browser writes directly), queue ↔
thumbnail-worker (untrusted file content enters a privileged process),
user content ↔ app origin (`/view`, `/share` rendered on `app.teamboard.io`),
tenant ↔ tenant (shared Postgres/S3).

## 1. SSRF via Import from URL — Critical

**Where:** "Import from URL" section; `POST /api/projects/:id/documents/import`.
Server fetches any user URL with Faraday, redirects enabled, from the
production VPC under the `teamboard-app` task role.

**Attack:** an authenticated user (any tenant, any plan) imports
`http://169.254.169.254/latest/meta-data/iam/security-credentials/teamboard-app`
(or an ECS task metadata endpoint `169.254.170.2/v2/credentials/...`), then
views the resulting document. The body is the role's temporary AWS
credentials, which have access to the docs bucket (all tenants), SQS, and
Secrets Manager. Variants: internal services in the VPC, a public URL that
302s to an internal address, DNS rebinding. The doc even advertises
"internal wiki exports" as a use case.

**Expected mitigations:** perform fetches in an isolated egress worker with
no IAM role and no route to private ranges; resolve-then-connect with
private/loopback/link-local/metadata IP blocking (IPv4 and IPv6) re-checked on
each redirect (or redirects disabled); http(s) only; IMDSv2/hop limit as
backstop; size and time caps.

**Testable requirement example:** import of `169.254.169.254`, `[::1]`,
`127.0.0.1.nip.io`, and a public URL redirecting to `10.0.0.1` all fail with
no outbound connection to those addresses.

## 2. Enumerable unauthenticated share links (cross-tenant IDOR) — Critical/High

**Where:** `GET /share/:doc_id`, "Share links are simply
`/share/<id>`", `id BIGSERIAL`.

**Attack:** an anonymous user (no account) iterates `/share/1..N`. Every
document with `shared = true` across all tenants is downloadable; IDs are
sequential so the space is tiny and also leaks document volume per tenant.
Disabling sharing then re-enabling restores the same URL, so a link can't be
rotated after it leaks. A strong run also notes that the design doesn't
state whether `/view` checks `tenant_id` against the session (the API table
says "scoped to the caller's current workspace" for `/api/*` but `/view` is
not under `/api`) and asks or flags it.

**Expected mitigations:** a separate share token (≥128-bit CSPRNG) stored per
share, revocable and optionally expiring, URL `/share/<token>`; 404 for
unknown/revoked tokens; rate limiting on `/share/*`; explicit tenant check on
`/view` in the data-access layer.

**Testable requirement example:** `/share/<integer id>` returns 404 even when
the document is shared; revoking a share invalidates its token; user in
tenant B requesting tenant A's `/documents/:id/view` gets 404.

## 3. Same-origin serving of user content with client Content-Type (stored XSS) — Critical/High

**Where:** "Inline viewing (`/view` and `/share`) streams the S3 object through
the app with `Content-Type` set to the stored `content_type`"; `content_type`
is "from the client's upload" (complete) or "from the response header"
(import). Admin console lives at `app.teamboard.io/admin` — same origin.

**Attack:** a user uploads `report.html` or an SVG with embedded script,
declared as `text/html` / `image/svg+xml`, and shares it or posts it in a task.
When a workspace member — or a Teamboard staff member using the admin
console — opens it, the script runs on `app.teamboard.io` with their session:
reads CSRF tokens, calls APIs as them, and for staff, drives the admin
console. Via `/share`, the attacker can also deliver it to anyone, under the
trusted domain (phishing). Import from URL lets an attacker set any content
type from their own server.

**Expected mitigations:** serve user content from a separate cookieless
registrable domain (e.g. `teamboard-usercontent.net`, not a subdomain);
server-side content type from a render allowlist after magic-byte sniffing;
`Content-Disposition: attachment` for everything else (HTML/SVG never inline
on the app origin); `X-Content-Type-Options: nosniff`; `CSP: sandbox;
default-src 'none'` on served files; admin console on its own origin.

**Testable requirement example:** uploading HTML with `Content-Type:
text/html` results in a response from the content domain with
`Content-Disposition: attachment` and `nosniff`; no request to the content
domain carries app session cookies.

## 4. Unsandboxed ImageMagick on every upload (untrusted file parsing) — High

**Where:** "Thumbnails and previews": `convert <input>[0]` on every upload and
import, distro package, **default policy**, SVG/PDF/Ghostscript enabled, in
the production VPC with the `teamboard-app` role.

**Attack:** a crafted file exploits ImageMagick/Ghostscript delegates (history:
ImageTragick CVE-2016-3714, Ghostscript `-dSAFER` bypasses, MVG/MSL/SVG coder
abuse, file-read via `text:`/`@` paths) for RCE or arbitrary file read inside a
worker that has AWS credentials for every tenant's documents and Secrets
Manager. Separately: decompression bombs / pixel floods (a small PNG declaring
100k×100k) exhaust memory and stall the shared queue for all tenants.

**Expected mitigations:** sandboxed worker (separate task role with access only
to the one object, no network or egress-only to S3 via VPC endpoint, no Secrets
Manager, read-only FS, non-root, seccomp, CPU/memory/time limits); restrictive
`policy.xml` (disable PS/EPS/PDF/XPS/MVG/MSL/URL/TEXT coders unless needed, set
width/height/area/memory limits); detect type by magic bytes and only
thumbnail an allowlist; consider a memory-safe library (libvips) for common
image types; per-tenant fair queuing.

## 5. Presigned uploads with no size/type limits or quota (cost/DoS) — Medium/High

**Where:** "Storage and uploads": presigned PUT, 1-hour expiry, "We aren't
setting a hard size limit for v1", no per-tenant quota; `upload-url` can be
called repeatedly; free plan gets the feature.

**Attack:** a free-plan account scripts `upload-url` and pushes multi-GB (S3
single PUT up to 5 GB) objects in a loop; storage and request costs land on
Teamboard. Abandoned uploads (URL issued, `complete` never called) are never
cleaned up or counted. Huge files also feed the thumbnail worker (item 4). A
presigned PUT without pinned Content-Type lets the client set any type on the
object.

**Expected mitigations:** presigned POST with `content-length-range` and pinned
key and Content-Type; per-plan file size cap; per-tenant storage quota checked
before issuing URLs; rate limit on `upload-url`; S3 lifecycle rule for objects
never completed; billing anomaly alerts as a backstop only.

## 6. No audit log of access, download, or sharing (repudiation) — Medium

**Where:** "Observability" lists metrics, 7-day Rails request logs, and Sentry
only. Nothing records who viewed, downloaded, shared, or unshared a document;
`/share` access is anonymous.

**Attack/impact:** an insider or compromised account shares a sensitive file
externally and unshares it after it's downloaded — no durable record of who
did it or who accessed it. After any incident in items 1-3, Teamboard can't
tell a tenant which documents were exposed beyond 7 days of request logs,
which also don't capture tenant/document semantics. Customers with
compliance needs will ask for this.

**Expected mitigations:** append-only audit events (actor, tenant, action
∈ {upload, view, download, share, unshare, delete}, doc ID, share token ID,
IP, user agent, timestamp) stored outside the actor's control with a
retention policy; tenant admins can query their own tenant's events.

## Rating expectations

Items 1-3 should be the top tier (Critical/High); items 4-5 High/Medium; item
6 Medium. Exact labels may differ, but a run that rates all six the same, or
rates the audit-log gap above the SSRF, fails the "ratings spread" check.
Extra valid findings (no virus scanning, CSRF on state-changing endpoints,
filename path traversal in the S3 key, XXE via SVG, mass assignment of
`tenant_id` in `complete`) are credit, not noise, if they are concrete.

## Fail conditions

- Generic STRIDE list ("Spoofing: attackers may impersonate users") with no
  reference to import, share links, `/view`, ImageMagick, or presigned URLs.
- Missing the SSRF, or describing it without the metadata/credentials or
  internal-network impact.
- Treating share links as fine because "the user chose to share it" without
  noticing the integer IDs are enumerable by anyone.
- No data-flow diagram, or a diagram with no trust boundaries marked.
- Mitigations stated as "validate input" / "sanitize files" with no location.
