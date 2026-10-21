---
name: threat-modeler
description: >
  Threat-models a design before it is built: assets, actors, a
  data-flow diagram with trust boundaries, STRIDE threats as concrete attacks,
  likelihood x impact ratings, mitigations, abuse cases, residual risk and
  testable security requirements. Use when asked to threat model a design doc
  or RFC, get security sign-off before code, find attack vectors or abuse
  cases, run STRIDE, ask what a malicious user or attacker could do, or set
  security requirements for uploads, previews, share links, URL import or
  tenant isolation. Do not use for architecture review of scale or cost (use
  system-design-reviewer), a code diff (use production-code-review), or
  auditing existing code for vulnerabilities (security-auditor).
license: MIT
compatibility: Text-based analysis of a design doc or description. No filesystem or network access required unless the design lives in a repo or connected tool.
metadata:
  category: security
  composes_with:
    - system-design-reviewer
    - feature-to-production
---

# Purpose

Find the ways a planned feature can be attacked while the fix is still a
design change, and turn each significant threat into a security requirement
the implementation must meet and a test that proves it does.

# When to use

- A design doc, RFC, or feature description exists and nothing (or little)
  is built yet, and someone asks to threat model it or "find the holes".
- A big change to an existing system adds a new trust boundary: a public
  endpoint, file upload/processing, server-side fetching of user URLs,
  sharing outside the tenant, webhooks/callbacks, a new third-party
  integration, or a new admin capability.
- As the security stage of `feature-to-production` before implementation,
  or alongside `system-design-reviewer` when the design has a security ask.

# When NOT to use

- General architecture review (scaling, consistency, cost, failure modes)
  with no security-specific ask — use `system-design-reviewer`; its security
  dimension is a short pass, not a threat model.
- A code diff or PR is under review — use `production-code-review`.
- The code already exists and the ask is to find vulnerabilities in it —
  that is an audit (`security-auditor`), not a threat model. A threat model
  can still precede a big change to it.
- A conceptual question ("what is STRIDE?") — answer it directly.

# Required inputs

- The design: doc, RFC, diagram, or a description of components, data
  stores, external services, and every way data enters and leaves.
- Tenancy and identity model: who the users are, how they authenticate, what
  separates one customer's data from another's.
- Deployment context if known: cloud provider, network layout, where admin
  tools live, which domains serve what.

If tenancy, auth, or hosting is unstated, write the assumption into the
model and list it as an open question. Do not model against a guessed setup
silently — the most severe threats usually live in those unstated details.

# Workflow

1. **Define scope.** Name what is in (the new feature and every component it
   touches) and out. List the entry points: every endpoint, upload, job,
   callback, and admin action the design adds.
2. **List assets.** What an attacker wants: tenant documents, credentials and
   session cookies, cloud credentials, internal network reach, compute
   budget, the audit trail. Rank the top three.
3. **List actors.** At minimum: anonymous internet user, authenticated user,
   user in another tenant, malicious insider/admin, compromised dependency or
   third-party service. Say what each can already reach.
4. **Draw the data flow.** Text or Mermaid. Every process, data store,
   external entity, and flow, with each **trust boundary** marked (internet ↔
   app, app ↔ worker, app ↔ object storage, app ↔ third party, tenant ↔
   tenant, user content ↔ app origin). Do not continue until every entry point
   from step 1 appears.
5. **Enumerate threats per element and per boundary-crossing flow** using
   STRIDE. Write each as an attack sentence: actor, action, element, result
   ("A user in tenant B iterates `/share/1..N` and downloads tenant A's
   documents"). A category name alone is not a threat. Trace server-side
   fetches, file parsing, and content serving end to end — they are skipped
   most often and cost the most.
6. **Rate each threat** likelihood (Low/Med/High) × impact (Low/Med/High),
   with a one-line justification each: who can do it, how hard it is, what
   it costs the victim. Ratings must spread; if they don't, re-justify.
7. **Map mitigations.** For every Medium-or-higher threat, name a specific
   mitigation and where it lives (component, layer, config). Prefer a design
   change that removes the attack (separate origin, signed token, allowlist,
   sandbox) over detection ("add monitoring"). Note when one mitigation
   covers several threats.
8. **Write abuse cases.** 3-6 short misuse stories crossing several elements
   ("free-tier account uploads 10,000 × 5 GB files via presigned URLs").
9. **Record residual risk.** Each accepted or partially mitigated threat:
   why it's accepted, what remains, and a named owner (role or team).
10. **Turn mitigations into security requirements and tests.** Each
    requirement is testable (`SR-n: share links require a ≥128-bit random
    token; integer IDs return 404`) and links to threat IDs, with at least
    one test case an implementer can write (input, expected result).
11. **Prioritize.** Order requirements must-have-before-launch,
    before-GA, and backlog by the ratings from step 6.

# Tool & resource guidance

- For step 5, read `references/stride-per-element.md` for the per-element
  prompts (which STRIDE categories apply to processes, stores, flows,
  external entities) and examples of attack sentences versus category names.
- If the design fetches URLs server-side, parses or thumbnails uploaded
  files, serves user content, exposes share links or object IDs, separates
  tenants in shared storage, or sends/receives webhooks, read
  `references/high-yield-threat-patterns.md` and check each pattern by name.
- If the design is in a repo, read the actual route/config files it names
  rather than trusting the doc's summary of them.

# Output contract

Produce `THREAT_MODEL.md` with these sections, in order:

- **Scope** — in, out, entry points.
- **Assets** — ranked.
- **Actors** — each with capabilities.
- **Data-flow diagram** — text or Mermaid, trust boundaries labelled.
- **Assumptions and open questions**
- **Threat table** — ID, element/flow, STRIDE category, attack sentence,
  likelihood, impact, rating, justification.
- **Mitigations** — mitigation, threat IDs covered, where it lives, design
  change vs. control.
- **Abuse cases**
- **Residual risk** — threat ID, what remains, why accepted, owner.
- **Security requirements and test cases** — SR ID, requirement, threat IDs,
  test case(s), priority tier.

# Quality checks

- [ ] Every entry point in scope appears in the data-flow diagram, and every
      boundary-crossing flow has at least one threat considered.
- [ ] Every threat names an actor, an action on a specific element, and a result.
- [ ] Ratings use at least two distinct levels, each with a justification.
- [ ] Every Medium+ threat maps to a mitigation with a location, or to a
      residual-risk entry with an owner.
- [ ] Every security requirement is testable and traces to threat IDs.
- [ ] Assumptions about tenancy, auth, and hosting are written down.

# Red flags

Stop and correct course if any of these are true:

- Your threat table contains rows like "Spoofing — attackers may impersonate users" with no element, actor, or mechanism.
- You are listing threats and have not yet drawn the data-flow diagram or marked a single trust boundary.
- Every threat is rated "High", or every threat has the same rating.
- A mitigation reads "validate input", "sanitize", or "use encryption" without saying which input, where, and against what rule.
- The design fetches URLs, processes uploaded files, or serves user content, and none of those paths has a threat row.
- A share link, object ID, or presigned URL is in the design and you haven't asked who can guess, enumerate, or reuse it.
- A security requirement can't be turned into a test ("the system shall be secure against XSS").

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "I'll run through the six STRIDE letters and that's the model." | STRIDE is a prompt, not an output. A category with no attack sentence gives the implementer nothing to build or test. |
| "The diagram is obvious from the doc; skip drawing it." | Threats live on boundary crossings. Without the boundaries drawn, the server-side fetch and the content-serving path are exactly what goes missing. |
| "Everything is high severity to be safe." | Uniform ratings make prioritization impossible and get the whole model ignored. Justify each rating; spread is the signal. |
| "We'll add monitoring and WAF rules." | Detection after the fact is not a mitigation for a design flaw. Prefer the change that removes the attack; use monitoring for what remains. |
| "Auth handles that." | Ask which check, on which request, against which tenant. Unauthenticated share routes, workers, and presigned URLs bypass the login check entirely. |
| "It's an internal service, so it's trusted." | An SSRF or a compromised dependency puts the attacker inside. Internal reach is an asset to protect, not a boundary to assume. |

# Edge cases

- **Design is a one-paragraph idea**: model what's there, mark assumptions
  heavily, and make open questions the main output — don't invent components.
- **Change to an existing system**: model only the new or changed elements and
  the boundaries they cross, but include existing elements the change exposes
  (e.g. an admin panel newly sharing an origin with user uploads).
- **Third-party SaaS owns a component**: treat it as an external entity;
  threats are about what you send it, what it sends back, and what happens
  if it's compromised.
- **Very low-stakes internal tool**: keep the model short, but still draw the
  boundaries — the low stakes must be a stated assumption, not an omission.
- **Team pushes back on a mitigation's cost**: record it as residual risk
  with an owner and the cheapest partial mitigation, not as silently dropped.

# References

- `references/stride-per-element.md` — STRIDE prompts per DFD element type
  and how to turn a category into a concrete attack sentence.
- `references/high-yield-threat-patterns.md` — SSRF, IDOR/enumeration,
  untrusted file parsing, same-origin user content, multi-tenant isolation,
  webhook/callback abuse, and resource exhaustion, with standard mitigations.
- `examples/outbound-webhooks-threat-model.md` — a full worked
  `THREAT_MODEL.md` for an outbound-webhooks feature.
