---
name: security-auditor
description: >
  Audits an existing codebase or service for vulnerabilities: maps the attack
  surface, runs dependency, secret and dangerous-sink scans as leads, traces
  every lead from untrusted input to the risky operation, checks per-object
  authorization, and ranks confirmed findings by reachability and impact with
  fixes. Use when asked for a security audit, vulnerability assessment, pentest
  prep, or compliance check of a service before launch or going live — SQL
  injection, IDOR, whether a logged-in customer can see another company's data,
  path traversal, hardcoded secrets, weak password hashing, OWASP Top 10. Do not
  use for one pull request or diff (use
  production-code-review), or for a design not yet built (threat-modeler).
license: MIT
compatibility: Needs read access to the whole codebase and its dependency manifests. Shell access helps for running local scanners; network optional (dependency advisories).
metadata:
  category: security
  composes_with:
    - production-code-review
    - debugging-investigator
---

# Purpose

Find the vulnerabilities in an existing service that untrusted users can
actually reach, back each one with reachability evidence from the code, and
hand back a ranked, fixable list — without scanner noise and without
claiming coverage that was never checked.

# When to use

- A service is about to launch, go through an external pentest, or face a
  compliance review (SOC 2, ISO 27001, PCI) and needs a security audit first.
- Asked to "find vulnerabilities", "check this for SQL injection / IDOR /
  secrets", or "is this app secure" about code that already exists.
- After an incident or a scanner report, to confirm which leads are real.

# When NOT to use

- The question is about one PR or diff before merge — use
  `production-code-review`; its security dimension covers the change.
- The system is still a design or RFC with no code — threat-model the design
  (`threat-modeler`) instead of auditing code that doesn't exist.
- The ask is to understand or map an unfamiliar codebase with no security
  question — that is `repo-architect`.
- Asked to test a system the user does not own or operate. Decline; audit
  only code and environments the user controls.

# Required inputs

- The codebase (or the service directory within a monorepo) and its
  dependency manifests/lockfiles.
- What "in scope" means: which services, which deployment (dev config vs the
  production entrypoint), and who the untrusted actors are (anonymous users,
  logged-in tenants, admins). If unstated, assume every network-reachable
  route and every authenticated non-admin user is untrusted, and say so.

# Workflow

1. **Scope.** Write down what is audited, the commit/version, the deployment
   entrypoint that runs in production, and the trust boundaries. Anything
   excluded goes straight into the not-covered list.
2. **Map the attack surface.** Enumerate every entry point (routes, RPC
   handlers, CLI args, queue consumers, file uploads, webhooks) with its auth
   requirement. Record the authn mechanism (sessions, tokens, signing key),
   the authz model (tenants, roles, ownership columns), data stores, file and
   network I/O, where secrets come from, and third-party dependencies.
3. **Run automated checks as leads.** Run whatever exists locally:
   `pip-audit -r requirements.txt` / `npm audit` / `osv-scanner`, a secret
   grep (`SECRET`, `PASSWORD`, `TOKEN`, `KEY =`, private-key headers), and a
   dangerous-sink grep (f-string or `+` SQL, `.format(` near `execute`,
   `eval`/`exec`, `shell=True`, `os.system`, `yaml.load`, `pickle.loads`,
   `os.path.join`/`open`/`send_file` on request data, `render_template_string`,
   outbound HTTP to user-supplied URLs). If a tool is unavailable, say so and
   check that class manually. Every hit is a lead, not a finding.
4. **Trace each lead.** For every lead, follow the data from the untrusted
   source (request arg, body, header, upload, DB field written by another
   tenant) to the risky operation, noting each transformation: casts,
   allowlists, parameter binding, normalization. Discard the lead with a
   one-line reason if a control neutralizes it; keep those reasons.
5. **Record reachability evidence.** For each surviving lead, write down the
   route and parameter where untrusted input enters, the code path it
   follows (function by function), and the line where it reaches the risky
   operation without the safeguard (no parameter binding, no ownership check,
   no path normalization). Establish this by reading the code — never by
   testing systems you don't own. If any link in the chain is uncertain, it
   is a LIKELY RISK, not a CONFIRMED finding.
6. **Check authorization on every object access.** For each route that takes
   an ID, filename, or key, confirm the handler (or query) checks that the
   object belongs to the caller's tenant/user — not just that someone is
   logged in. Compare sibling handlers: one that checks ownership next to one
   that doesn't is the classic IDOR.
7. **Check configuration and crypto.** Password storage (bcrypt/scrypt/
   argon2 with salt, not MD5/SHA-1/unsalted), session signing key source,
   cookie flags (`Secure`, `HttpOnly`, `SameSite`), debug modes and which
   entrypoint enables them, error and stack-trace leakage, TLS assumptions,
   CORS, and rate limiting on login.
8. **Rank by reachability x impact.** Assign Critical/High/Medium/Low from
   who can reach it, what precondition it needs, and what it yields — with a
   one-line justification. Never rank by the vulnerability class's name.
9. **Specify a fix per finding** — the specific code change (bind this
   query's parameters, add `account_id` to this WHERE, switch to
   `yaml.safe_load`), plus any rotation needed for exposed secrets.
10. **Write the not-covered list.** Areas, classes, and tools not checked,
    and why. Then write `SECURITY_AUDIT.md`. Do not modify the code unless
    the user asked for fixes to be applied.

# Tool & resource guidance

- Before assigning severities, read `references/severity-rubric.md`; it has
  worked examples of the same class landing at different severities.
- When writing fixes, read `references/secure-fix-patterns.md` so each fix
  is the standard safe pattern, not a blocklist or an escaping hack.
- Prefer reading code over running the app. If you do run it, run it locally
  against throwaway data. Scanner output is input to step 4, never output.
- Use grep for call sites of every risky function; a sink used in one place
  you checked may be used in three you didn't.

# Output contract

Write `SECURITY_AUDIT.md` with these sections, in order:

- **Scope & attack surface** — what was audited (version, entrypoint), trust
  boundaries, and the entry-point table (route, method, auth required,
  untrusted inputs).
- **Findings summary** — a table: ID, severity, title, location, status
  (CONFIRMED / LIKELY RISK), ranked most severe first.
- **Finding details** — per finding: location (file:function), reachability
  evidence (entry route and parameter, code path, the unguarded line),
  impact, severity justification, and fix.
- **Leads ruled out** — scanner hits and suspicious code that were traced and
  found safe, each with the control that neutralizes it.
- **Not covered** — what was not checked and why (tools unavailable,
  out-of-scope services, infra, runtime config).

# Quality checks

- [ ] Every CONFIRMED finding names its entry route, code path, and the
      unguarded line.
- [ ] Every route taking an object identifier was checked for ownership.
- [ ] Each severity names reachability (anonymous / any user / admin) and
      impact, not just the class.
- [ ] Each finding has a specific fix; exposed secrets include rotation.
- [ ] "Leads ruled out" exists and covers the scary-looking code that is safe.
- [ ] "Not covered" is non-empty or explicitly justified as empty.
- [ ] No source file was edited unless the user asked.

# Red flags

Stop and correct course if any of these are true:

- A finding cites a grep or scanner hit but has no trace from a request
  parameter to the risky operation.
- You checked that routes require login but have not compared each object
  lookup against the caller's tenant or user.
- A severity reads "SQL injection, therefore Critical" with no statement of
  who can reach it.
- You are about to write "no issues found" and the report has no list of
  what was checked.
- You flagged a parameterized query as injectable because the SQL is long or
  user input is nearby.
- You are editing application code, or sending requests to a host the user
  doesn't own, and nobody asked you to.
- The dependency section copies a CVE list without checking whether the
  vulnerable function is called.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "The scanner flagged it, so it's a vulnerability." | Scanners match patterns, not data flow. Unconfirmed hits waste the fix budget and train the team to ignore the report. Trace it or list it as a lead. |
| "Every route has `@login_required`, so access control is fine." | Authentication says who you are; authorization says what you may touch. IDOR lives in the query that fetches by ID alone. |
| "It's SQL injection — that's always Critical." | Severity is reachability times impact. Admin-only injection on a read replica differs from anonymous injection on the users table. Justify it. |
| "I can't confirm it without testing production." | Reachability is established from the code path. Testing systems you don't own is never part of the audit. |
| "It's just the dev config; prod is different." | Check which entrypoint production uses. If the secret lives in the repo, it's leaked regardless of which config loads it. |
| "I'll fix these while I'm in the code." | The deliverable is the audit. Unrequested edits mix findings with changes nobody reviewed. Write the fix in the report. |
| "Nothing obvious turned up, so it's clean." | "Clean" without a coverage list is unfalsifiable. State what was checked and what wasn't. |

# Edge cases

- **No scanners installed or no network**: do the dependency check manually
  against known-vulnerable versions you can justify, mark it in Not covered,
  and continue — the manual trace is the core of the audit anyway.
- **Large codebase**: audit the attack surface breadth-first, go deep on
  auth, money, file I/O and deserialization, and list unvisited modules.
- **Secret found in code**: report it once with location and the rotation
  step; do not repeat the secret value in the report beyond a short prefix.
- **Vulnerable dependency, unreachable function**: report as Low or as a
  ruled-out lead with the reason, not at the advisory's CVSS score.
- **User asks for fixes too**: finish the audit first, then apply fixes as a
  separate step, and re-trace each path to show the safeguard is now present.
- **Finding needs runtime config you can't see** (WAF, proxy limits): mark it
  LIKELY RISK and say what config would confirm or refute it.

# References

- `references/severity-rubric.md` — Critical/High/Medium/Low definitions with
  worked examples.
- `references/secure-fix-patterns.md` — standard safe code per vulnerability
  class.
- `examples/document-portal-audit.md` — a full worked `SECURITY_AUDIT.md`
  for an Express document-sharing service.
