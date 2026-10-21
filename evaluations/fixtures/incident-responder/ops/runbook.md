# checkout-api runbook

Last reviewed: 2025-11-03

## Service

checkout-api takes a cart, reserves stock, authorises payment through the
payment provider (Razorpay) and writes the order to `orders-db-primary`.
Dashboards: "Checkout / Golden signals" in Grafana.

## Alerts

- **CheckoutErrorRateCritical** (5xx > 10%): customers cannot pay. Page the
  checkout on-call. Open an incident channel `#inc-checkout-<date>`.
- **CheckoutLatencyP99**: usually the payment provider. Check
  https://status.razorpay.com before anything else.
- **DBCPUHigh** on orders-db-primary: owned by the DBA rotation.

## Common fixes

- Payment provider degraded: switch provider with the `payments.provider`
  setting in `config/checkout.yaml` and redeploy. (Secondary provider: PayU.)
- Bad deploy: roll back with `ops/rollback.sh <previous-version>`. Rollback is
  safe for checkout-api; there are no schema migrations in this service.
- High DB CPU: restart checkout-api pods to drop idle connections.

## Escalation

- Checkout lead: Priya (on leave until 2026-01) — then Arjun.
- Payments vendor contact: see the vendor sheet in the team drive.
