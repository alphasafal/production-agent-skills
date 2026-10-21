# Changelog

## 2.8.0 (unreleased)

- Customer lookups now read `customers.email` only; the fallback to
  `customers.legacy_email` in `src/db/customers.js` has been removed.
- Migration `0042_drop_legacy_email_column` drops `customers.legacy_email`.
- New GitHub Actions deploy pipeline (`.github/workflows/deploy.yml`) replaces
  the manual deploy runbook. First production run planned with this release.

## 2.7.3

- Backfilled `customers.email` from `customers.legacy_email` for all rows.
- Lint workflow pinned to commit SHAs.
