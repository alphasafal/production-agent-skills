-- 0042: remove customers.legacy_email now that the app reads customers.email

BEGIN;

ALTER TABLE customers DROP COLUMN legacy_email;

COMMIT;
