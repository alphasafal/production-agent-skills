"""Cart pricing for the checkout service.

Items are dicts: {"sku": str, "unit_price": float, "qty": int}.
Coupons are dicts: {"code": str, "kind": "percent", "value": number}.
"""


def _subtotal(items):
    total = 0.0
    for item in items:
        if item["qty"] < 0:
            raise ValueError(f"negative quantity for {item['sku']}")
        total += item["unit_price"] * item["qty"]
    return total


def _apply_percent(amount, percent):
    if not 0 < percent <= 100:
        raise ValueError(f"percent coupon must be between 0 and 100, got {percent}")
    return amount * (100 - percent) / 100


def cart_total(items, coupons=None):
    """Return the amount to charge for a cart, after coupons."""
    coupons = coupons or []
    if len(coupons) > 1:
        raise ValueError("only one coupon per cart")

    total = _subtotal(items)
    for coupon in coupons:
        if coupon["kind"] != "percent":
            raise ValueError(f"unsupported coupon kind: {coupon['kind']}")
        total = _apply_percent(total, coupon["value"])

    return round(total, 2)
