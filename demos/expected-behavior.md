# Expected Behavior Reference

What a *correct* run of each demo prompt (see `demo-prompts.md`) should
look like, for judging a live demo or recording against. These mirror each
skill's `evaluations/workflows/<skill>.json` scenario at a glance —
consult that file for the full grading detail.

| Skill | A correct run should... | A red flag would be... |
|---|---|---|
| repo-architect | Read actual files/imports before describing structure; produce ARCHITECTURE.md/MODULE_MAP.md/etc.; touch no code | Describing structure from directory names alone, or editing a file "while looking around" |
| debugging-investigator | Reproduce the duplicate-payment race, form 2+ hypotheses, reject at least one with evidence, confirm the concurrency mechanism, add a regression test | Proposing a fix ("add error handling") before reproducing or gathering any evidence |
| production-code-review | Flag the missing idempotency protection as P0/P1 with the specific line, classify FACT vs LIKELY RISK, end with a merge recommendation matching the severity | Flat list of nitpicks with no severity, or "looks good to me" on a diff with a real concurrency bug |
| system-design-reviewer | Flag the hash-collision gap and missing cache explicitly, state assumptions since no scale target was given | Generic "consider adding monitoring" advice with no scenario-specific risk named |
| data-scientist | Run profiling/leakage checks via the bundled scripts, catch `cancellation_reason` as leakage, establish a baseline before any model claim | Training a model directly on the leaky column, or reporting accuracy with no baseline |
| research-to-decision | Define criteria before scoring, mark unverified claims as assumptions, produce an ADR stating what's given up | Confident claims with no source and no assumption flag |
| product-manager | Identify the riskiest unproven assumption, cut at least one plausible feature from v1 with a stated reason | Scoping v1 to include every feature the request could justify |
| feature-to-production | Write the 429/Retry-After test before/alongside implementation, produce a deployment checklist and a rollback plan specific to this change | Calling it "done" once it runs once locally, with no test and no rollback plan |

For a live audience-facing demo, the debugging-investigator scenario reads
best on camera: it has a clear wrong answer (guess-and-check), a clear
right answer (evidence → confirmed root cause → minimal fix → regression
test), and a runnable fixture (`examples/02-debug-a-failure/sample-app/`).
