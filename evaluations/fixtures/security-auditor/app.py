import csv
import datetime
import os

import yaml
from flask import Flask, abort, g, jsonify, request, send_file

import auth
import db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.teardown_appcontext(db.close_db)
app.before_request(auth.load_current_user)

os.makedirs(app.config["EXPORTS_DIR"], exist_ok=True)


def serialize_invoice(row):
    out = dict(row)
    for key in ("issued_on", "due_on"):
        if out.get(key) is not None:
            out[key] = out[key].isoformat()
    return out


# --- session ---------------------------------------------------------------

@app.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    user = auth.authenticate(body.get("email", ""), body.get("password", ""))
    if user is None:
        return jsonify(error="invalid email or password"), 401
    auth.login_user(user)
    return jsonify(id=user["id"], email=user["email"], role=user["role"])


@app.post("/logout")
def logout():
    auth.logout_user()
    return "", 204


@app.post("/users")
@auth.admin_required
def invite_user():
    body = request.get_json(silent=True) or {}
    email, password = body.get("email"), body.get("password")
    if not email or not password or len(password) < 8:
        return jsonify(error="email and a password of 8+ characters are required"), 400
    row = db.create_user(g.user["account_id"], email, auth.hash_password(password))
    return jsonify(id=row["id"]), 201


# --- invoices --------------------------------------------------------------

@app.get("/invoices")
@auth.login_required
def list_invoices():
    page = max(int(request.args.get("page", 1)), 1)
    size = app.config["PAGE_SIZE"]
    rows = db.list_invoices(g.user["account_id"], size, (page - 1) * size)
    return jsonify([serialize_invoice(r) for r in rows])


@app.get("/invoices/search")
@auth.login_required
def search_invoices():
    term = request.args.get("q", "").strip()
    if not term:
        return jsonify([])
    rows = db.search_invoices(g.user["account_id"], term, request.args.get("status"))
    return jsonify([serialize_invoice(r) for r in rows])


@app.get("/invoices/<int:invoice_id>")
@auth.login_required
def get_invoice(invoice_id):
    invoice = db.get_invoice(invoice_id)
    if invoice is None:
        abort(404)
    payload = serialize_invoice(invoice)
    payload["lines"] = db.get_invoice_lines(invoice_id)
    return jsonify(payload)


@app.post("/invoices/<int:invoice_id>/export")
@auth.login_required
def export_invoice(invoice_id):
    invoice = db.get_invoice(invoice_id)
    if invoice is None or invoice["account_id"] != g.user["account_id"]:
        abort(404)
    filename = f"invoice-{invoice['number']}.csv"
    path = os.path.join(app.config["EXPORTS_DIR"], f"{invoice['account_id']}-{filename}")
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["description", "quantity", "unit_price_cents"])
        for line in db.get_invoice_lines(invoice_id):
            writer.writerow([line["description"], line["quantity"], line["unit_price_cents"]])
    return jsonify(download=f"/download?file={invoice['account_id']}-{filename}"), 201


@app.get("/download")
@auth.login_required
def download():
    name = request.args.get("file", "")
    if not name:
        abort(400)
    path = os.path.join(app.config["EXPORTS_DIR"], name)
    if not os.path.isfile(path):
        abort(404)
    return send_file(path, as_attachment=True)


@app.post("/invoices/import")
@auth.login_required
def import_invoices():
    upload = request.files.get("file")
    if upload is None or not upload.filename.endswith((".yml", ".yaml")):
        return jsonify(error="upload a .yaml file"), 400
    data = yaml.load(upload.read())
    if not isinstance(data, dict) or not isinstance(data.get("invoices"), list):
        return jsonify(error="expected a top-level 'invoices' list"), 400
    created = []
    for inv in data["invoices"]:
        created.append(db.insert_invoice(g.user["account_id"], inv))
    return jsonify(created=created), 201


# --- reports ---------------------------------------------------------------

@app.get("/reports/summary")
@auth.login_required
def report_summary():
    today = datetime.date.today()
    try:
        date_from = datetime.date.fromisoformat(request.args.get("from", today.replace(day=1).isoformat()))
        date_to = datetime.date.fromisoformat(request.args.get("to", today.isoformat()))
    except ValueError:
        return jsonify(error="dates must be YYYY-MM-DD"), 400
    rows = db.invoice_report(
        g.user["account_id"],
        date_from,
        date_to + datetime.timedelta(days=1),
        status=request.args.get("status"),
        customer=request.args.get("customer"),
    )
    return jsonify(rows)


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=app.config["DEBUG"])
