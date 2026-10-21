# checkout-pricing

Cart total calculation used by the checkout service. `cart_total(items,
coupons)` in `pricing.py` is the only public entry point; the checkout API
calls it and charges the returned amount (a float, in rupees).

## Running tests

No third-party dependencies. From this directory:

```bash
python -m unittest                         # full suite
python -m unittest test_pricing.CartTotalTest.test_percent_coupon   # one test
```
