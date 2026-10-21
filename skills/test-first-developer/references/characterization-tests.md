# Characterization tests

A characterization test records what code does today, right or wrong, so
you can change it and know exactly which behaviors moved. Use these before
changing untested or legacy code (workflow step 3) and before any refactor
of code whose rules you don't fully know.

## When you need them

- The function you are about to change has no tests, or its tests cover
  only the happy path.
- You are refactoring, so behavior must stay identical.
- Callers you can't see (other services, reports, scripts) depend on the
  output format.

If good tests already cover the area, skip this and rely on them.

## How to write one

1. **Pick the public entry point** callers use. Characterize that, not the
   helpers behind it.
2. **Choose inputs** that exercise each branch you can see in the code:
   each `if`, each loop count of 0, 1 and many, each exception raised.
   Add real inputs from logs, fixtures or bug reports if you have them.
3. **Write the test with a placeholder expectation** you know is wrong
   (for example, `assertEqual(result, "CHANGE_ME")`).
4. **Run it.** The failure message shows the actual output.
5. **Paste the actual output into the assertion** and rerun. It passes.
   That value is now pinned.
6. **Name it for what it shows**: `test_current_rounding_truncates_half_cent`,
   not `test_legacy_1`.

The placeholder step matters: it means you got the expected value from the
code's actual output, not from what you assumed the code does.

## Pinned behavior that looks wrong

You will find outputs that look like bugs. Do not fix them in the
characterization step.

- Pin them as they are, with a comment saying what looks off and why.
- Raise them in `TEST_LOG.md` and in your reply.
- Change them only if the task asks for it, as its own red-green case with
  the old test updated and the reason recorded.

Fixing a quirk while pinning it hides a behavior change inside a
"no-change" step, and a caller may rely on that quirk.

## Golden-file / snapshot variant

For large outputs (rendered HTML, reports, JSON payloads), write the
current output to a file once and compare against it. Keep these few and
targeted: a snapshot that changes on every edit gets regenerated without
anyone reading the diff, and then it pins nothing.

## Seams for hard-to-test code

If the code can't be called in a test (it reads the clock, the network or
global config directly), find the smallest seam:

- pass the dependency in as a parameter with the current behavior as the
  default,
- or wrap the call in a function you can replace in the test.

Make that change alone, with the suite green before and after, before you
start characterizing. See `test-doubles.md` for what to put in the seam.

## When you're done

The characterization tests stay in the suite. After the change, any of them
that fail show a behavior you changed: either the change was intended (the
ticket says so — update the test and record it) or it was not (fix the
code).
