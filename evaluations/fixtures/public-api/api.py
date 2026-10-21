"""A tiny public JSON API, used as the codebase for the feature-to-production
workflow eval ("add rate limiting ... ship it"). Pure standard library.

Requests are plain dicts so the handler is testable without a server:
    handle({"method": "GET", "path": "/v1/widgets", "headers": {"X-API-Key": "k1"}})
returns (status_code, body_dict, response_headers).
"""
from __future__ import annotations

import time

API_KEYS = {"k1": "acme", "k2": "globex"}

WIDGETS = [
    {"id": 1, "name": "sprocket"},
    {"id": 2, "name": "gear"},
]


def _now() -> float:
    return time.monotonic()


def list_widgets(request: dict) -> tuple[int, dict, dict]:
    return 200, {"widgets": WIDGETS}, {}


def get_widget(request: dict, widget_id: int) -> tuple[int, dict, dict]:
    for w in WIDGETS:
        if w["id"] == widget_id:
            return 200, w, {}
    return 404, {"error": "not found"}, {}


def handle(request: dict) -> tuple[int, dict, dict]:
    key = request.get("headers", {}).get("X-API-Key")
    if key not in API_KEYS:
        return 401, {"error": "invalid or missing API key"}, {}

    path = request.get("path", "")
    if request.get("method") != "GET":
        return 405, {"error": "method not allowed"}, {}
    if path == "/v1/widgets":
        return list_widgets(request)
    if path.startswith("/v1/widgets/"):
        try:
            return get_widget(request, int(path.rsplit("/", 1)[1]))
        except ValueError:
            return 400, {"error": "bad widget id"}, {}
    return 404, {"error": "not found"}, {}


if __name__ == "__main__":
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import json

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, body, headers = handle(
                {"method": "GET", "path": self.path, "headers": dict(self.headers)}
            )
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            for k, v in headers.items():
                self.send_header(k, str(v))
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
