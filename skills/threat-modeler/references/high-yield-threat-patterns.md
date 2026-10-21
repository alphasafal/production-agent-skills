# High-yield threat patterns

These patterns account for a large share of real incidents in web and SaaS
designs, and each one is easy to miss in a design doc because the feature
reads as harmless ("import from a link", "share a document"). When the design
has the trigger, check the pattern by name and write it into the threat table
either as a threat or as "considered, not applicable because ...".

## 1. Server-side request forgery (SSRF)

**Trigger:** the server fetches a URL a user supplies or influences — import
from URL, link previews, webhooks the user configures, avatar-from-URL, PDF
rendering of user HTML, OAuth/OIDC discovery URLs.

**Attack:** the user supplies `http://169.254.169.254/latest/meta-data/iam/...`
(cloud metadata), `http://localhost:6379`, `http://10.0.0.5/admin`, a hostname
that resolves to a private IP, or a public URL that redirects to one. The
server's network position and credentials become the attacker's.

**Impact:** cloud credential theft (often full account compromise), access to
internal admin services, port scanning, reading internal-only data.

**Standard mitigations (design-level first):**
- Run fetches from an isolated egress service or worker with no cloud
  credentials and no route to internal networks (separate VPC/subnet, egress
  proxy).
- Resolve the hostname, reject private, loopback, link-local, and metadata
  ranges (IPv4 and IPv6), then connect to the resolved IP (prevents DNS
  rebinding). Re-check on every redirect, or disable redirects.
- Allow only `https` (and `http` if needed) schemes; block `file:`, `gopher:`,
  `ftp:`, etc.
- Enforce IMDSv2 / metadata hop limits at the platform level as a backstop.
- Cap response size, time, and content type.

**Tests:** fetch of `169.254.169.254`, `[::1]`, `127.0.0.1.nip.io`, a public URL
that 302s to `http://10.0.0.1` — all rejected.

## 2. IDOR and enumeration

**Trigger:** objects addressed by ID in URLs or bodies; share links; public
or "anyone with the link" access; sequential or timestamp-derived IDs.

**Attack:** change the ID; iterate the range; harvest every object across
tenants. Unauthenticated share routes are the worst case — no login, no rate
limit tied to an account.

**Standard mitigations:**
- Authorization check on every object load: object's tenant and ACL vs. the
  caller, enforced in the data-access layer, not per handler.
- Share links carry an unguessable token (≥128 bits from a CSPRNG), separate
  from the object ID, revocable, optionally expiring, scoped to one object
  and permission level.
- Non-sequential public identifiers; 404 (not 403) on unauthorized access.
- Rate limits and alerting on high-volume 404s per IP/token.

**Tests:** user in tenant B requests tenant A's object by ID → 404;
`/share/<integer>` → 404; revoked token → 404.

## 3. Untrusted file parsing

**Trigger:** thumbnails, previews, OCR, virus scanning, document conversion,
metadata extraction, archive unpacking — anything that parses user files with
ImageMagick, Ghostscript, LibreOffice, ffmpeg, PDF libraries, XML parsers.

**Attack:** crafted file exploits the parser (ImageMagick has a long history:
ImageTragick, delegate abuse via MVG/SVG/PS); XXE in SVG/DOCX; zip slip;
decompression bombs and pixel floods that exhaust memory/CPU.

**Standard mitigations:**
- Parse in a sandbox: separate container/microVM, no network, no cloud
  credentials, read-only filesystem, seccomp, non-root, CPU/memory/time limits.
- Restrict formats by magic bytes, not extension or client Content-Type;
  disable dangerous coders (ImageMagick `policy.xml`: block PS, EPS, PDF, MVG,
  MSL, SVG, URL coders; set `width`, `height`, `area`, `memory` limits).
- Process asynchronously with a per-tenant queue so failures don't block uploads.
- Keep parser dependencies patched; treat it as an internet-facing service.

**Tests:** upload a decompression bomb → job killed at limit, upload still
recorded; MVG/PS file → rejected; worker has no route to metadata endpoint.

## 4. Same-origin user content

**Trigger:** the app serves user-uploaded files (HTML, SVG, PDF, XML, even
"images") from its own domain or a domain sharing cookies with it.

**Attack:** upload `evil.svg` or `evil.html` with `Content-Type: text/html`;
send the link to an admin. Script runs in the app's origin, reads or uses the
session, calls APIs as the victim. If the admin panel shares the origin or
parent domain, this is admin takeover.

**Standard mitigations:**
- Serve user content from a separate, cookieless registrable domain
  (`usercontent-example.net`, not a subdomain of the app domain).
- Server sets Content-Type from a server-side allowlist after sniffing; never
  echo the client-supplied type.
- `Content-Disposition: attachment` for anything not on a render allowlist;
  `X-Content-Type-Options: nosniff`; restrictive CSP (`sandbox`,
  `default-src 'none'`) on served files.
- Admin tooling on its own origin with its own session.

**Tests:** upload HTML/SVG with `text/html` → served from content domain as
attachment with `nosniff`; no app cookies sent to the content domain.

## 5. Multi-tenant isolation

**Trigger:** shared database, bucket, cache, search index, queue, or worker
pool across tenants.

**Attack:** missing `tenant_id` filter on one query; cache key without tenant;
bucket keys guessable across tenants; search index returns other tenants' hits;
a background job runs with an all-tenant role.

**Standard mitigations:** tenant scoping enforced centrally (row-level
security, a repository layer that requires tenant context, per-tenant key
prefixes with IAM conditions); tenant in every cache key; per-tenant quotas
and fair queuing; cross-tenant tests in CI.

## 6. Webhook and callback abuse

**Trigger:** inbound webhooks from providers; outbound webhooks to
customer-configured URLs; OAuth redirects; "notify me at this URL".

**Attack (inbound):** forged callbacks without signature verification; replay
of a valid signed event. **Attack (outbound):** SSRF via the configured URL
(pattern 1); secret leakage in payloads; retry storms against a victim host.

**Standard mitigations:** verify HMAC signatures with constant-time compare
and a timestamp window; idempotency on event ID; outbound through the SSRF-safe
egress path; per-endpoint signing secrets; capped retries with backoff;
redirect-URI exact-match allowlists for OAuth.

## 7. Resource exhaustion and cost abuse

**Trigger:** presigned uploads, user-triggered jobs, AI/LLM calls, outbound
email/SMS, exports, anything billed per use.

**Attack:** unlimited object size or count via presigned URLs; job fan-out;
storage or egress billing run up on a free account; one tenant starving others.

**Standard mitigations:** presigned POST policies with `content-length-range`
and pinned key and Content-Type; per-tenant storage and request quotas checked
before issuing URLs; rate limits per account and per IP; lifecycle rules for
abandoned uploads; billing alerts as a backstop, not the control.

## 8. Missing audit trail

**Trigger:** any access to sensitive data, permission or sharing changes,
admin actions.

**Attack:** not an attack on its own — it is what turns every other incident
into "we can't tell what was taken". Insiders and compromised accounts deny
actions.

**Standard mitigations:** append-only audit events (actor, tenant, action,
object, timestamp, IP, user agent, share token ID) for view, download, share,
permission change, delete; stored where the actor can't modify it; retention
set by policy; queryable by tenant admins for their own tenant.
