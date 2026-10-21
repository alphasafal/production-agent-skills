# Worked example: adding a late-fee rule test-first

**Prompt:** "Rentals returned late should be charged a late fee: 3-day grace
period, then 25 per day, capped at 500. Members pay half. Just add it to
`rentalCharge`, we need it this week."

The repo is a small Node service (`src/billing.js`, `test/billing.test.js`).
Abridged run: the transcript commands are shown first, then the
`TEST_LOG.md` it produced.

---

## Step 1 — how this repo tests

- `package.json`: `"test": "node --test test/"`. No Jest, no Mocha.
- `.github/workflows/ci.yml` runs `npm test` on Node 20.
- Single test: `node --test --test-name-pattern="late fee" test/`.
- Existing tests use `node:test` + `node:assert/strict`, one `describe` per
  exported function, names in plain English.

## Step 2-3 — baseline and pinned behavior

`npm test` → `# pass 6  # fail 0`. Existing behaviors next to the change:
daily rate × days rented, a damage surcharge, and an error on a return date
before the start date. All three have tests already; nothing to
characterize.

---

# TEST_LOG.md — rentalCharge late fees

## Test command

- Full suite: `npm test` (→ `node --test test/`), from `package.json`;
  CI runs the same.
- Single test: `node --test --test-name-pattern="<name>" test/`.

## Baseline

`npm test` before changes: 6 pass, 0 fail.

## Cases

Late days = days returned after `dueDate`. Fee computed on whole days.

| # | Input | Expected | Rule |
|---|---|---|---|
| 1 | returned 2 days late | fee 0 | grace period |
| 2 | returned 3 days late | fee 0 | grace boundary — *assumption:* "3-day grace" means days 1-3 are free |
| 3 | returned 4 days late | fee 25 | first charged day |
| 4 | returned 23 days late | fee 500 | 20 charged days = cap exactly |
| 5 | returned 40 days late | fee 500 | cap holds above the limit |
| 6 | member, 5 days late | fee 25 | half of 50 |
| 7 | member, 40 days late | fee 250 | half applied after the cap — *assumption* |
| 8 | returned on time | fee 0, total unchanged | regression |
| 9 | return before start | throws RangeError | existing error path |

Cases 8 and 9 are covered by existing tests; run them, don't duplicate.

## Red → green log

| # | Test | Red | Green | Full suite after |
|---|---|---|---|---|
| 1 | `no late fee inside the grace period` | `AssertionError: undefined !== 0` (`lateFee` field missing) | pass | 7/7 |
| 2 | `no late fee on the last grace day` | passed on first run (fee was still a constant 0) — rechecked after case 3 by mutation: grace set to 2, test failed `25 !== 0`, reverted | pass | 8/8 |
| 3 | `charges 25 for the first day after grace` | `AssertionError: 0 !== 25` | pass | 9/9 |
| 4 | `late fee reaches the cap at 23 days` | passed on first run (cap not yet written, 20 × 25 is already 500) — verified by mutation: rate changed to 26, test failed `520 !== 500`, reverted | pass | 10/10 |
| 5 | `late fee never exceeds 500` | `AssertionError: 925 !== 500` | pass | 11/11 |
| 6 | `members pay half the late fee` | `AssertionError: 50 !== 25` | pass | 12/12 |
| 7 | `member discount applies to the capped fee` | `AssertionError: 462.5 !== 250` (case 6 halved the daily rate before the cap) | pass | 13/13 |

Case 4 note: an exact-at-cap input can't distinguish "capped" from
"uncapped", so case 5 is the real cap test. Case 4 stays as the boundary.

## Refactors

- Extracted `lateDays(dueDate, returnedAt)` inside `billing.js` (not
  exported; tests still go through `rentalCharge`). Suite 13/13.
- Replaced the five near-identical non-member late-fee tests with one
  `for (const tc of cases) test(tc.name, ...)` loop. Suite 13/13.

## Existing tests changed

None.

## Final full suite

`npm test` after the last edit: `# tests 13  # pass 13  # fail 0`.

---

**Reply to the user (summary):** Late fees are in `rentalCharge` with seven
new tests. Two assumptions to confirm: the 3rd late day is still free, and
the member half-price applies after the 500 cap (so members max out at
250). Full suite green.
