# Widgets API

Small public JSON API. Clients authenticate with an `X-API-Key` header.

- `GET /v1/widgets` — list widgets
- `GET /v1/widgets/<id>` — one widget

Run tests: `python -m unittest`
Run locally: `python api.py` (serves on 127.0.0.1:8000)
