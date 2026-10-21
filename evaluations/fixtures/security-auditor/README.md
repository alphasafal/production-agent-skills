# invoicing-service

Small multi-tenant invoicing API. Each customer business is an **account**;
users belong to one account and should only ever see that account's invoices.

## Endpoints

| Method | Path | Notes |
|---|---|---|
| POST | `/login`, `/logout` | JSON body `{email, password}`; session cookie |
| POST | `/users` | admin only; invite a user into your account |
| GET | `/invoices` | paginated list for your account |
| GET | `/invoices/search?q=&status=` | search by customer name or invoice number |
| GET | `/invoices/<id>` | invoice with line items |
| POST | `/invoices/<id>/export` | writes a CSV into `exports/`, returns a download link |
| GET | `/download?file=` | fetch an exported CSV |
| POST | `/invoices/import` | multipart upload of a YAML file with an `invoices:` list |
| GET | `/reports/summary?from=&to=&status=&customer=` | billed / paid / outstanding per customer |

## Schema (Postgres)

`accounts(id, name)`, `users(id, account_id, email, password_hash, role)`,
`invoices(id, account_id, number, customer_name, customer_email, total_cents, currency, status, issued_on, due_on)`,
`invoice_lines(invoice_id, position, description, quantity, unit_price_cents)`,
`payments(id, invoice_id, amount_cents, status)`.

## Running

```bash
pip install -r requirements.txt
python app.py                      # dev
gunicorn -w 4 -b 0.0.0.0:8000 app:app   # prod
```
