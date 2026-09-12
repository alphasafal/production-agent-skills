# Bug Spoiler — don't read before attempting the investigation

## Root cause

`process_payment` in `app.py` performs a **check-then-act race**:

```python
if order.status != "pending":      # (1) check
    return "already paid, skipping"

_charge_card(order_id)             # (2) act — the "charge"
store.record_payment(order_id)
order.status = "paid"              # (3) act — the write that would prevent re-entry
```

Two threads calling `process_payment("order-1")` at roughly the same time
both pass check (1) while `order.status` is still `"pending"` — neither
has reached step (3) yet, which is the only place that would stop the
other. `_charge_card`'s `time.sleep(0.05)` widens this window enough that
it reproduces on essentially every run, which is what makes this a good
demo (a real production race might only show up 1 in a few thousand
requests, exactly the kind of thing `debugging-investigator`'s
`concurrency-debugging.md` reference is about).

## Why `self._lock_for_bookkeeping_only` doesn't help

It only protects the `_payments` list append from a data-structure-
corruption race (two threads appending at the exact same instant). It does
nothing to prevent both threads from getting *past* the status check in
the first place — that's the actual bug, and it's a common trap: a lock
exists in the code, so it's easy to assume "this is already synchronized"
without checking *what* it actually protects.

## The fix

Protect the whole read-check-act sequence with one lock (a real system
would use a DB-level `SELECT ... FOR UPDATE` on the order row instead of
an in-process lock, since a real payment service usually isn't single-process):

```python
_order_locks: dict[str, threading.Lock] = {}

def process_payment(order_id: str) -> str:
    lock = _order_locks.setdefault(order_id, threading.Lock())
    with lock:
        order = store.get_order(order_id)
        if order.status != "pending":
            return "already paid, skipping"
        _charge_card(order_id)
        store.record_payment(order_id)
        order.status = "paid"
        return "charged"
```

## Regression test

```python
def test_concurrent_payment_requests_charge_once():
    store.create_order("order-test")
    threads = [threading.Thread(target=lambda: process_payment("order-test")) for _ in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert store.payment_count("order-test") == 1
```

This fails against the original `app.py` and passes after the fix above.
