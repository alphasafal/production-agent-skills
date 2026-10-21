---
name: test-first-developer
description: >
  Drives code changes test-first: finds the repo's test runner, lists cases
  (boundaries, bad input, error paths), writes one test that must go red,
  writes minimal code to pass, refactors on green, and ends with the full
  suite and TEST_LOG.md. Use when asked to do TDD or red-green-refactor,
  write unit tests first, cover untested or legacy code, pin behavior with
  characterization specs before a refactor, find coverage gaps, or change a
  business rule such as pricing, fees, discounts or validation without
  breaking existing behavior, including rushed just-write-the-code asks. Do
  not use for a bug with an unknown cause (use debugging-investigator) or
  shipping a feature with deploy and rollback (feature-to-production).
license: MIT
compatibility: Needs filesystem and shell access to edit code and run the project's test suite. No network required beyond what the project's own tests need.
metadata:
  category: engineering
  composes_with:
    - feature-to-production
    - debugging-investigator
---

# Purpose

Make every behavior change provable. Each new case gets a test that is seen
failing for the right reason before any code is written for it, then seen
passing, and the whole suite is green at the end. The run leaves a log that
shows this happened, not just a claim that it did.

# When to use

- A logic change with clear rules: a new pricing, discount, validation,
  parsing, scheduling or permission rule in an existing module.
- Asked for TDD, red-green-refactor, or "write the tests first".
- Adding tests to untested or legacy code, or pinning behavior before a
  refactor (characterization tests).
- Test-strategy requests: what to test, where the coverage gaps are, which
  cases a function is missing.
- A rushed "just get it done" on rule-heavy code: the tests are how you get
  it done without breaking the existing rules.

# When NOT to use

- Something is broken and the cause is unknown — use
  `debugging-investigator`. It also writes a reproducing test, but its job
  is finding the cause.
- Shipping a whole feature end to end with design, review, deploy and
  rollback plan — use `feature-to-production`, which calls this workflow
  for its test step.
- A conceptual question ("what's the difference between a mock and a
  stub?") — just answer it.
- A change with no behavior to assert (renaming a file, editing copy, bumping
  a comment) — make it and run the suite once.

# Required inputs

- The rules or behavior to add or change, as stated by the user or ticket.
- The repository, with a way to run its tests.

If a rule is ambiguous (rounding mode, order of operations, what happens at
the limit), write down the interpretation you will test and say so in the
log; ask only if two readings lead to different money or data outcomes and
nothing in the code or docs decides it.

# Workflow

1. **Discover how this repo tests.** Read the README, manifest files
   (`pyproject.toml`, `setup.cfg`, `package.json`, `go.mod`, `Cargo.toml`,
   `Makefile`), test runner config (`pytest.ini`, `jest.config.*`,
   `vitest.config.*`), and the CI workflow. Note the full-suite command and
   how to run one test. Read two existing tests to learn naming, fixtures
   and assertion style. Never assume a runner the repo doesn't use.
2. **Run the full suite before touching anything.** Record the result. If
   it is already red, stop and report which tests fail; do not build on a
   red baseline without saying so.
3. **Pin what must not change.** List the existing behaviors near your
   change (from tests and from reading the code). If one matters and has no
   test, write a characterization test that asserts today's actual output,
   run it, and confirm it passes before changing code.
4. **Write the case list.** Turn each rule into concrete input → expected
   output cases: the normal case, each boundary (at, just below, just above
   the limit), invalid input, error paths, ordering and interaction between
   rules, and rounding or precision where numbers are involved. Put the list
   in `TEST_LOG.md` before writing any test.
5. **Red.** Write ONE test for the next case, through the public interface
   (the function, endpoint or CLI callers use). Run only that test. It must
   fail with an assertion about behavior — wrong value, missing exception.
   An import error, typo or fixture crash is not red; fix it and rerun.
   Copy the failure line into the log.
6. **Green.** Write the minimum code that makes that test pass. Run it,
   then run the full suite so you know no existing test broke. Log both.
7. **Refactor.** With everything green, remove duplication or clarify names
   in code and tests. Rerun the full suite after each refactor.
8. **Repeat 5-7** case by case until the list is done. A case that passes
   the first time you run it is either already covered or the test is
   wrong: break the code on purpose for a second to confirm the test can
   fail, then note it in the log as "passed on first run — verified by
   mutation".
9. **Finish with the full suite** using the repo's own command, after the
   last edit. Paste the summary line into the log.
10. **Write `TEST_LOG.md`** per the output contract.

**Hard rule:** no implementation code for a case until its test has been
seen failing. Never delete, skip or loosen an existing assertion to get to
green; if the ticket truly changes an existing rule, update that test in its
own step, say which rule changed, and cite the ticket line that changes it.

# Tool & resource guidance

- When writing the case list, read `references/test-design-patterns.md` for
  boundary values, equivalence classes, table-driven tests and
  arrange-act-assert.
- If the code has no tests, or you are about to refactor code you didn't
  write, read `references/characterization-tests.md` before step 3.
- If the code under test talks to a database, network, clock, filesystem or
  randomness, read `references/test-doubles.md` before writing a fake,
  stub or mock.
- Use the narrowest run command for red and green (one test by name), and
  the full-suite command for the baseline, after green, and at the end.

# Output contract

The code change and its tests, plus `TEST_LOG.md` with these sections:

- **Test command** — the full-suite and single-test commands, and where
  they came from (README, CI file, config).
- **Baseline** — full-suite result before any change.
- **Cases** — the numbered case list, each with input, expected output and
  the rule it comes from; assumptions for ambiguous rules marked.
- **Red → green log** — per case: test name, the red failure line, the
  green result, and the full-suite result after green.
- **Refactors** — what changed and the suite result after each.
- **Existing tests changed** — none, or each one with the ticket rule that
  required it.
- **Final full suite** — command and summary line, run after the last edit.

# Quality checks

- [ ] The test command came from the repo, not from a default guess.
- [ ] Every case in the list has a test, and every new test maps to a case.
- [ ] Every new test has a recorded red run that failed on an assertion.
- [ ] Boundaries, invalid input and rule interactions are in the case list.
- [ ] Tests call the public interface; none import private helpers.
- [ ] No existing assertion was removed or weakened without a cited rule.
- [ ] The final full-suite run happened after the last code edit.

# Red flags

Stop and correct course if any of these are true:

- You wrote implementation code for a case whose test you have not yet run
  and seen fail.
- A new test passed on its first run and you moved on without checking it
  can fail.
- The "red" run failed with ImportError, NameError or a syntax error.
- A test asserts only that a mock was called, not what the caller gets back.
- A test imports an underscore-prefixed helper instead of the public entry point.
- You edited code after the last full-suite run and are about to say done.
- You are deleting, skipping or relaxing an existing assertion (`assertEqual`
  to `assertAlmostEqual`, exact to `>=`) so the suite goes green.
- You typed `pytest` or `npm test` without checking the repo uses it.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "It's too simple to test." | Simple rules carry the boundary bugs: off-by-one limits, negative totals, a cent of rounding. The test is three lines; the refund is not. |
| "I'll add tests after the code works." | Tests written after the code assert what the code does, not what the rule says. They pass by construction and catch nothing. |
| "I tested it manually in the REPL." | A REPL check covers one input once and disappears. It protects nothing on the next change and leaves no evidence. |
| "The user said just get it done, so skip the tests." | Done means the rules hold and nothing else broke. On rule-heavy code the tests are the fastest way to show that; say so and keep them small. |
| "Coverage is already 80%." | Coverage counts lines executed, not rules checked. The new branch you are adding is in the other 20% until a test hits it. |
| "This old test conflicts with the new code, I'll delete it." | That test is the spec for an existing rule. Change it only when the ticket changes that rule, and record which line says so. |
| "The test failed, that counts as red." | It counts only if it failed on the behavior. A missing import fails every time and proves nothing about the code. |

# Edge cases

- **Suite already failing**: record the failing tests in the baseline, do
  not fix unrelated failures silently, and make sure your cases are
  judged against the tests that were green.
- **No test infrastructure at all**: use the language's standard runner
  (`unittest`, `go test`, `cargo test`, `node --test`), say that you chose
  it, and keep the setup to one file.
- **Rule is ambiguous**: pick an interpretation, write the test for it,
  mark it as an assumption in Cases, and call it out in your reply.
- **Floating-point money**: test values that land on a half cent and decide
  the rounding mode explicitly; prefer `Decimal` or integer cents if the
  module can change without breaking callers.
- **Slow or external dependency**: put a fake or stub at that boundary only
  (`references/test-doubles.md`); keep your own logic real.
- **Test-strategy request with no code change**: produce the case list and
  coverage gaps in `TEST_LOG.md`, mark which are untested, and write the
  tests only if asked.

# References

- `references/test-design-patterns.md` — boundaries, equivalence classes,
  table-driven tests, arrange-act-assert, naming.
- `references/characterization-tests.md` — pinning legacy behavior before
  changing it.
- `references/test-doubles.md` — fake vs stub vs mock vs spy, and when each
  is acceptable.
- `examples/late-fee-rule.md` — a full worked run with its `TEST_LOG.md`.
