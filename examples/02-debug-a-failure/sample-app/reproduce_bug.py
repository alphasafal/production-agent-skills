#!/usr/bin/env python3
"""Fire two concurrent payment requests for the same order and report the result.

Usage: python reproduce_bug.py
"""
from __future__ import annotations

import threading

from app import process_payment, store


def main() -> int:
    store.create_order("order-1")

    results: list[str] = []

    def worker():
        results.append(process_payment("order-1"))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    count = store.payment_count("order-1")
    print(f"Worker results: {results}")
    print(f"Payments recorded for order-1: {count}")

    if count > 1:
        print("BUG REPRODUCED: order-1 was charged more than once.")
        return 1
    print("No duplicate charge this run (the race is timing-dependent — try again if this happens).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
