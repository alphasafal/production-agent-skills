---
name: debugging-investigator
description: >
  Investigates software failures using evidence-driven debugging: reproduction,
  hypothesis generation and ranking, targeted hypothesis testing, root-cause
  identification, minimal fixes, and regression verification. Use when something
  is broken or wrong and the cause is unknown: bugs, errors or exceptions being
  thrown, crashes, memory leaks or OOMs, hangs, failing or flaky tests, wrong or
  mismatched numbers, users being logged out,
  works-locally-but-not-in-production, intermittent errors, production
  incidents, or performance regressions — whenever asked to investigate why. Do
  not use for writing new features, general code review with no reported
  failure, or answering conceptual questions about how something works (e.g.
  "what is a stack trace" or "explain this error type").
license: MIT
compatibility: >
  Needs shell/filesystem access to reproduce and run tests. Log/metrics/tracing
  tool access (e.g. via MCP) is helpful for distributed-systems and production
  cases but not required for local reproduction.
metadata:
  category: engineering
  composes_with:
    - production-code-review
    - repo-architect
---

# Purpose

Turn debugging into an auditable, evidence-driven investigation instead of a
sequence of speculative edits. Every claim about the cause of a bug must be
backed by observed evidence before it is acted on.

# When to use

- A bug, crash, failing test, or incident has been reported and the cause is
  not yet known.
- Behavior changed after a deploy, dependency upgrade, or config change and
  the trigger isn't obvious from the diff alone.
- "Works on my machine" / intermittent / hard-to-reproduce failures.

# When NOT to use

- The user is asking a conceptual question ("what is a race condition?") with
  no actual failure to investigate — just answer it.
- The task is "add feature X" with no reported defect.
- The root cause is already known and stated by the user, and they've only
  asked for the fix to be applied — implement it directly, referencing this
  skill's regression-check step only.

# Required inputs

- A description of the observed failure (error message, stack trace, failing
  test name, or behavioral symptom).
- Access to reproduce it: a repo, a failing test command, logs, or a way to
  exercise the code path.

If these are missing, the first workflow step (OBSERVE) is how you get them —
ask the user rather than guessing.

# Workflow

Work through these steps in order. Do not skip from OBSERVE straight to a fix.

1. **OBSERVE** — Record the exact symptom: error text, stack trace, failing
   assertion, or metric anomaly. Note when it started and what changed around
   that time (deploy, dependency bump, config, data shape).
2. **REPRODUCE** — Get the failure to happen on demand, with the smallest
   possible trigger (a failing test, a curl command, a script). If it can't be
   reproduced yet, say so explicitly and treat "make it reproducible" as the
   current goal rather than guessing at a fix.
3. **MINIMIZE** — Strip the reproduction down to the smallest input/code path
   that still triggers it. This narrows the hypothesis space before you form any.
4. **COLLECT EVIDENCE** — Read logs, stack traces, git blame/history on the
   suspect area, relevant tests, and (if available) traces/metrics. Evidence
   here means something you directly observed, not something you assume.
5. **FORM HYPOTHESES** — List 2-4 concrete, falsifiable explanations for the
   evidence. A hypothesis must name a specific mechanism ("the retry wrapper
   double-submits on timeout"), not a vague area ("something in the payment code").
6. **RANK HYPOTHESES** — Order by how well each explains *all* the observed
   evidence (not just some of it) and how cheap it is to test.
7. **TEST HYPOTHESES** — For the top-ranked hypothesis, find or construct a
   check that would prove or disprove it (a targeted log line, a debugger
   breakpoint, a unit test that isolates the mechanism). A hypothesis is only
   **CONFIRMED** once a specific piece of evidence supports it; otherwise mark
   it **REJECTED** with the disproving evidence and move to the next one.
8. **IDENTIFY ROOT CAUSE** — State the confirmed mechanism, not just the
   symptom. "Null pointer on line 42" is a symptom; "the cache is read before
   the async warmup completes on cold start" is a root cause.
9. **IMPLEMENT MINIMAL FIX** — Fix the confirmed mechanism with the smallest
   change that addresses it. Do not bundle in unrelated cleanup.
10. **RUN REGRESSION CHECK** — Run the existing test suite (or the relevant
    subset) plus a new test that reproduces the original failure and now
    passes. If no such test existed, add one.
11. **EXPLAIN ROOT CAUSE** — Summarize what happened, why, and how the fix and
    new test prevent recurrence.

**Hard rule:** never make a speculative change ("let me try changing this and
see if it helps") in place of steps 4-8. If you're tempted to guess, that's a
signal to go collect more evidence instead.

# Tool & resource guidance

- If the failure is in a browser/frontend context, read
  `references/web-debugging.md` before forming hypotheses.
- If the failure involves query results, transactions, or migrations, read
  `references/database-debugging.md`.
- If the failure involves timeouts, retries, or cross-service calls, read
  `references/network-debugging.md`.
- If the symptom is intermittent and load- or timing-dependent, read
  `references/concurrency-debugging.md`.
- If the system spans multiple services and you have trace/log tooling
  available, read `references/distributed-systems-debugging.md`.
- If the complaint is about latency, throughput, or resource usage rather
  than incorrect output, read `references/performance-debugging.md`.

Use whatever tools give you real evidence: running tests, reading logs,
querying observability tools (via MCP if connected), git history/blame. Prefer
the cheapest tool that can actually confirm or reject the current hypothesis.

# Output contract

Produce `DEBUG_REPORT.md` (or an equivalent structured summary if the
environment has no file output) with these sections, in order:

- **Symptoms** — what was observed, verbatim where possible.
- **Reproduction** — the minimal steps/command that trigger it.
- **Evidence** — what was actually collected (logs, traces, test output).
- **Rejected hypotheses** — each with the evidence that disproved it.
- **Confirmed root cause** — the mechanism, with supporting evidence.
- **Minimal fix** — what changed and why it's sufficient.
- **Regression protection** — the test(s) added or run to confirm the fix
  holds and prevent recurrence.

# Quality checks

- [ ] The reported root cause is a mechanism, not a restatement of the symptom.
- [ ] At least one hypothesis was explicitly rejected with evidence (or the
      first hypothesis tested was confirmed on the first try — state that too).
- [ ] The fix is minimal and scoped to the confirmed cause.
- [ ] A regression test exists and fails against the pre-fix code, passes after.
- [ ] No step was skipped silently — if reproduction wasn't possible, that's
      stated, not glossed over.

# Red flags

Stop and correct course if any of these are true:

- You are editing code and cannot yet name the exact command that reproduces the failure.
- Your hypothesis names an area ("something in the payment code") instead of a mechanism.
- You have one hypothesis and have not written down what evidence would reject it.
- The fix adds a retry, a try/except, a sleep, or a null check, and you cannot say why the bad state happens.
- The "fix" diff also renames, reformats, or refactors unrelated code.
- You are about to say "fixed" and no test failed before your change and passes after it.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "It's obviously the X, I'll just fix it." | Obvious causes are the ones most often wrong. If it's obvious, confirming it costs one check — do the check. |
| "I can't reproduce it, so I'll make a defensive fix." | Then the goal is reproduction, not a fix. A defensive change you can't verify hides the bug and makes the next report harder to debug. |
| "Adding a retry / try-catch makes it go away." | Making a symptom go away is not a root cause. Retries around a race usually make duplicates *more* likely. |
| "The user is in a hurry — skip the regression test." | Without a failing-then-passing test you can't show the fix works, and the bug can silently return. The test is the shortest proof you have. |
| "While I'm in here I'll clean this up too." | Bundled cleanup makes the fix harder to review, harder to revert, and blurs which change actually fixed the bug. |

# Edge cases

- **Can't reproduce at all**: say so, report what evidence exists, and propose
  the next piece of instrumentation/evidence needed rather than guessing.
- **Multiple contributing causes**: report each with its own evidence rather
  than collapsing them into one "root cause."
- **Fix requires a larger architectural change**: implement the minimal safe
  fix now, and note the larger follow-up as a separate recommendation — don't
  silently expand scope.
- **Flaky/non-deterministic failures**: treat "reproduces N% of the time under
  condition X" as a valid, evidence-backed reproduction; read
  `references/concurrency-debugging.md`.

# References

See `examples/duplicate-payment-investigation.md` for a full worked example
of this workflow's output, end to end.
