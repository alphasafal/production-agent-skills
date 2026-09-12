"""Tiny in-memory order/payment service — intentionally buggy.

Pure standard library, no network, no external dependencies. Simulates a
payment endpoint that reads an order's status, "charges" it (with a small
artificial delay standing in for a real network call to a payment
provider), then marks it paid — as three separate, unsynchronized steps.

Run `python reproduce_bug.py` to see the bug in action. Don't peek at
BUG_SPOILER.md until you've tried to find it yourself.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class Order:
    id: str
    status: str = "pending"


class OrderStore:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._payments: list[str] = []
        self._lock_for_bookkeeping_only = threading.Lock()

    def create_order(self, order_id: str) -> None:
        self._orders[order_id] = Order(id=order_id)

    def get_order(self, order_id: str) -> Order:
        return self._orders[order_id]

    def record_payment(self, order_id: str) -> None:
        # Bookkeeping only — does NOT protect the read-check-charge-write
        # sequence below, which is the actual bug.
        with self._lock_for_bookkeeping_only:
            self._payments.append(order_id)

    def payment_count(self, order_id: str) -> int:
        return sum(1 for p in self._payments if p == order_id)


store = OrderStore()


def _charge_card(order_id: str) -> None:
    """Stands in for a real call to a payment provider's API."""
    time.sleep(0.05)


def process_payment(order_id: str) -> str:
    """Process a payment for an order. This is the buggy handler."""
    order = store.get_order(order_id)

    if order.status != "pending":
        return "already paid, skipping"

    _charge_card(order_id)
    store.record_payment(order_id)
    order.status = "paid"
    return "charged"
