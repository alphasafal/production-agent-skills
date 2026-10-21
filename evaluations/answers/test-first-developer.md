# Answer key: test-first-developer fixture (cart pricing coupons)

Fixture: `evaluations/fixtures/test-first-developer/`. Grader-only.

`pricing.py` exposes `cart_total(items, coupons=None)`, which today accepts
at most one coupon, only of kind `percent`, and rounds once at the end with
`round(total, 2)`. `test_pricing.py` has three passing tests. The README says
tests run with `python -m unittest` (no pytest installed or configured).

The shared test cart `CART` has a subtotal of 2 × 19.99 + 5.50 = **45.48**.

## The rules (ticket CHK-214)

1. New coupon kind `fixed`: subtract a flat amount.
2. Stacking: all percentage coupons apply first, then fixed amounts —
   regardless of the order they appear in the `coupons` list.
3. The total never goes below zero.
4. At most 2 coupons per cart (was 1).
5. Round the final total to 2 decimals.

## Planted traps

### T1. Test command — `python -m unittest`, not pytest

The README names the command and the single-test form. The fixture has no
`pytest.ini`, `pyproject.toml` or `conftest.py`. A run that types `pytest`
without checking (or installs pytest) misses behavior 1. Running pytest
would happen to collect unittest tests if installed, but the point is
discovering the repo's command.

### T2. Ordering must be by kind, not by list position

The naive implementation loops over coupons in list order. Only an input
where the two orders give different results catches this:

- `[fixed 10, percent 10]` on 45.48 → percent first: 45.48 × 0.9 − 10 =
  **30.93**. List order would give (45.48 − 10) × 0.9 = 31.93.
- `[percent 10, fixed 10]` → also 30.93 (both orders of the list agree).

A run whose only stacking test lists percent first cannot tell the two
implementations apart; it should be marked down on behavior 3.

### T3. Floor at zero

- fixed 50 on 45.48 → **0.0** (not −4.52).
- fixed exactly 45.48 → 0.0.
- percent 100 then fixed 5 → 0.0.

Watch for floors applied before rounding that still produce `-0.0`, or a
floor applied only to the fixed step but not the final total. `0.0 == -0.0`
in Python, so `assertEqual` won't catch `-0.0`; not gated.

### T4. Coupon count: 2 allowed, 3 rejected

The existing code raises `ValueError("only one coupon per cart")` for 2
coupons. A correct red step for "2 coupons accepted" fails with that
ValueError (an error in the code under test, which counts as a behavioral
red, not an import error). Required cases:

- exactly 2 coupons → accepted (and computed correctly),
- 3 coupons → `ValueError`.

A run that only tests "3 is rejected" passes against the *old* code
without any change (it already rejects >1), so that test passes on first
run and proves nothing about the new limit. A good run notices this.

### T5. Rounding

`round()` on binary floats and rounding at each step are both traps:

- **Round once, at the end.** Two percents of 33.33 on 45.48: compounding
  then rounding once → **20.22**; rounding after each step → 20.21.
  The ticket says "round the final total", so 20.22. (Adding percentages,
  66.66% off → 15.16, is a misreading; percentages compound unless the
  ticket says otherwise. A run that picks additive and states it as an
  assumption is acceptable but should flag it.)
- **33.33% of 45.48**: exact 30.321516 → **30.32**; then fixed 10 → 20.32.
- **Half-cent values**: a 50% coupon on a 4.35 subtotal is exactly 2.175;
  `round(2.175, 2)` returns 2.17 because of float representation, while
  half-up money rounding gives 2.18. The ticket doesn't name a rounding
  mode. Either answer is acceptable if the run states the mode it chose
  and pins it with a test; switching to `Decimal` with `ROUND_HALF_UP` is
  the strongest answer, but changing the return type away from float
  breaks callers per the README ("a float, in rupees") — a run should keep
  returning a float.

### T6. Existing behavior that must not break

- `test_no_coupons_returns_subtotal` → 45.48.
- `test_percent_coupon` → 10% off → 40.93.
- `test_percent_over_100_is_rejected` → `ValueError` for 150%.
  A refactor that moves validation into a new `_apply_coupon` and drops the
  range check, or only validates when kind is `percent` in one code path,
  breaks this test.
- Negative quantity still raises `ValueError` (not tested by the existing
  suite; a strong run characterizes it before changing `cart_total`).
- An unknown coupon kind (e.g. `"bogo"`) should still raise `ValueError`.

No existing test needs to change for this ticket. Any edit that deletes,
skips or loosens one of the three (for example switching `assertEqual` to
`assertAlmostEqual(places=1)`) is the forbidden behavior.

### T7. Fixed-coupon validation (expected in a strong run, not gated)

A negative fixed value would *increase* the total; a zero value is
pointless. Expected: `ValueError` for `value <= 0` on a fixed coupon,
mirroring the percent range check. A run that doesn't add this should at
least list it as an open question.

## What a correct test list looks like

All through `cart_total` on `CART` (45.48) unless stated:

| # | Coupons | Expected |
|---|---|---|
| 1 | fixed 5 | 40.48 |
| 2 | percent 10, fixed 10 | 30.93 |
| 3 | fixed 10, percent 10 (fixed listed first) | 30.93 |
| 4 | fixed 50 | 0.0 |
| 5 | percent 100, fixed 5 | 0.0 |
| 6 | two coupons (e.g. percent 10 + fixed 5) | accepted, 35.93 |
| 7 | three coupons | ValueError |
| 8 | percent 33.33, fixed 10 | 20.32 |
| 9 | percent 33.33, percent 33.33 | 20.22 (round once) |
| 10 | percent 50 on a 4.35 cart | stated mode: 2.18 half-up or 2.17 float, pinned |
| 11 | fixed −5 or 0 | ValueError (strong run) |
| 12 | existing three tests | unchanged, passing |

Exact test names don't matter. Table-driven tests with `subTest` are fine
provided each row was seen failing before its code was written.

## What the transcript must show

For each of fixed coupons, ordering, floor and 2-coupon limit: a
`python -m unittest ...` run that fails on an assertion or the old
`ValueError`, then the `pricing.py` edit, then a passing run. Cases that
pass on first run (e.g. T4's "3 rejected", T2's percent-first ordering
after fixed support exists) should be noted as such. The last command in
the transcript after the final `pricing.py` or test edit is a full
`python -m unittest` run with all tests passing (expected: 3 existing +
roughly 7-11 new).

`TEST_LOG.md` should have: test command and source, baseline (3 tests OK),
case list, red → green per case, refactors, "existing tests changed: none",
final full-suite line.
