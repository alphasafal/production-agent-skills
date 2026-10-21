# Test doubles

What to substitute for a real dependency in a test, and when substituting
is the wrong call. Read this before writing a fake, stub or mock.

## The default: use the real thing

Your own pure code — calculations, parsing, validation, domain objects —
runs fast and deterministically. Call it for real. Replacing your own
collaborators with mocks means the test checks how the code is wired today,
so it breaks on refactors and passes when the logic is wrong.

Substitute only at a boundary that is:

- **slow** (a real database, a large file, a model call),
- **external** (network APIs, payment providers, email, queues you don't own),
- **non-deterministic** (clock, random numbers, UUIDs, thread timing), or
- **destructive** (charges money, sends messages, deletes data).

## The kinds, and when each is OK

| Double | What it is | Use it when |
|---|---|---|
| **Fake** | A working, simplified implementation: an in-memory repository, a local SMTP sink, a dict-backed cache. | You need the dependency to behave realistically across several calls. Usually the best choice for storage. |
| **Stub** | Returns canned answers: `clock.now()` always returns 2026-03-01 09:00. | You need to control an input the code reads (time, an API response, a feature flag). |
| **Spy** | Records calls so you can inspect them afterwards, while behaving like a stub or the real thing. | The observable outcome *is* the call: "an email was sent to the customer with the invoice number". |
| **Mock** | Pre-programmed with expectations and fails if they're not met. | Rarely. Only when the interaction itself is the contract and a spy can't express it. |

## Asserting through a double

Assert on what a caller can observe:

- With a fake: the state of the fake afterwards (the order is in the
  in-memory repo with status `paid`).
- With a stub: the return value of the code under test given the stubbed
  input.
- With a spy: the content of the outgoing call (recipient, amount, ID),
  not just that a call happened.

A test whose only assertion is `mock.assert_called_once()` proves the code
called something. It does not prove the right amount, recipient or record —
which is the part that goes wrong.

## Common mistakes

- **Mocking the module under test.** If you patch the function you are
  testing, or the helper that holds its logic, the test runs your mock.
- **Patching where it's defined, not where it's used** (Python): patch
  `orders.send_email`, the name the code looks up, not
  `email_client.send_email`.
- **Stubbing to match the current bug.** A stub's canned response should
  match the real dependency's contract (status codes, field names, error
  shapes), taken from its docs or a recorded response.
- **A fake that drifts.** If you keep a fake, run the same contract tests
  against the fake and the real implementation occasionally so they stay
  in step.
- **Freezing time globally** when only one function reads the clock. Pass a
  clock in instead.

## Checklist before adding a double

- [ ] The dependency is slow, external, non-deterministic or destructive.
- [ ] The double sits at that boundary, not around my own logic.
- [ ] The test asserts on a result or on the content of an outgoing call.
- [ ] The double's responses match the real dependency's contract.
