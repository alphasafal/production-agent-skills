# Test design patterns

How to turn a rule into a case list that catches the bugs people actually
ship. Use this while writing the case list (workflow step 4).

## Equivalence classes

Split each input into groups the code should treat the same, and test one
representative per group. For a quantity field: negative, zero, one,
typical, and the maximum allowed. For a coupon list: empty, one, the
maximum allowed, one over the maximum. One test per class is enough; ten
tests inside the same class add run time, not confidence.

Classes come from the rule, not from the current code. If the ticket says
"orders over 500 ship free", the classes are below 500, exactly 500, and
above 500 — whatever the existing `if` statement happens to check.

## Boundary values

Bugs gather at the edges of classes. For every limit in a rule, test:

- exactly at the limit,
- one step below (one unit, one cent, one day, one item),
- one step above.

Read the rule's wording for which side the limit falls on: "at most 2"
includes 2, "more than 2" excludes it, "before the 15th" excludes the 15th.
Write the interpretation into the case so a reviewer can disagree with it.

Typical limits to look for: counts (max items, max retries), money floors
and caps (never below zero, discount capped at subtotal), dates (end of
month, leap day, time zone midnight), string lengths, and empty
collections.

## Rule interactions and ordering

When two rules apply to the same input, the order changes the result. Pick
inputs where the orders give different answers, or the test can't tell
them apart. Example: adding 18% tax and then a flat 40 shipping charge
gives a different total from adding shipping and then taxing it. A test
where both orders give the same answer (shipping of zero) proves nothing
about order.

Also test that each rule still works alone after the other is added.

## Precision and rounding

For money and measurements:

- Choose inputs whose exact result has more decimals than you keep, and at
  least one that lands exactly on a half (x.xx5). Binary floats round some
  half values down (`round(2.675, 2) == 2.67`), so this is where float bugs
  show up.
- Decide where rounding happens: per line, per step, or once at the end.
  Rounding at each step and rounding once give different totals; the rule
  should say which, and a test should pin it.
- Assert exact values with exact comparison. `assertAlmostEqual` with a
  loose tolerance hides the cent you are trying to get right.

## Invalid input and error paths

For every input, ask what happens when it is missing, the wrong type,
negative, zero, duplicated, or unknown (an unrecognized enum value). Decide
whether the right behavior is an exception, a validation error, or a safe
default, and test the specific exception type and, if callers rely on it,
the message.

## Table-driven tests

When many cases share the same shape (input → expected output), put them in
a table and loop. Each row needs a name so a failure says which case broke.

```python
CASES = [
    ("no coupon", [], 100.00),
    ("ten percent", [pct(10)], 90.00),
    ("percent then fixed", [pct(10), fixed(5)], 85.00),
]

def test_totals(self):
    for name, coupons, expected in CASES:
        with self.subTest(name):
            self.assertEqual(total(CART_100, coupons), expected)
```

In pytest use `@pytest.mark.parametrize` with `ids=`; in Go use a slice of
structs with `t.Run(tc.name, ...)`; in Jest use `test.each`.

Under test-first, add one row at a time and watch that row fail before
writing the code for it. Don't write the whole table up front and then
implement everything at once — that is test-after with extra steps.

## Arrange, act, assert

Each test has three parts, in this order, with one act:

- **Arrange** the input and any setup.
- **Act** by calling the public interface once.
- **Assert** on what a caller can observe: the return value, the raised
  error, the record written, the message sent.

Two acts in one test means two tests. Asserting on internal state (a
private field, a helper's return value) ties the test to the current
implementation and breaks on every refactor.

## Naming

Name the test after the behavior, so the failure line reads as a broken
rule: `test_total_never_goes_below_zero`, not `test_cart_3` or
`test_apply_fixed_helper`.

## What a good case list looks like

Numbered, one line per case, with input, expected output and the rule it
comes from. Mark assumptions.

Rule: "Orders of 500 or more ship free; otherwise 40 per parcel, max 3
parcels charged."

```
1. order 499.99, 1 parcel → 40               (below free-shipping limit)
2. order 500.00, 1 parcel → 0                (at the limit: "or more")
3. order 120, 3 parcels → 120                (3 parcels, at the cap)
4. order 120, 5 parcels → 120                (cap applies above 3)
5. order 120, 0 parcels → ValueError         (assumption: an order ships at least one parcel)
6. existing: express flag still adds 60      (regression)
```
