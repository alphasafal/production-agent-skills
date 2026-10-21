import unittest

from pricing import cart_total

CART = [
    {"sku": "TEA-ASSAM-250", "unit_price": 19.99, "qty": 2},
    {"sku": "MUG-STONE", "unit_price": 5.50, "qty": 1},
]


class CartTotalTest(unittest.TestCase):
    def test_no_coupons_returns_subtotal(self):
        self.assertEqual(cart_total(CART), 45.48)

    def test_percent_coupon(self):
        coupons = [{"code": "SPRING10", "kind": "percent", "value": 10}]
        self.assertEqual(cart_total(CART, coupons), 40.93)

    def test_percent_over_100_is_rejected(self):
        coupons = [{"code": "BROKEN", "kind": "percent", "value": 150}]
        with self.assertRaises(ValueError):
            cart_total(CART, coupons)


if __name__ == "__main__":
    unittest.main()
