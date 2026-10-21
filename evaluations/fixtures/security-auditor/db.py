import psycopg2
import psycopg2.extras
from flask import current_app, g


def get_db():
    if "db" not in g:
        cfg = current_app.config
        g.db = psycopg2.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            dbname=cfg["DB_NAME"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=None, one=False):
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def execute(sql, params=None, returning=False):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone() if returning else None
    conn.commit()
    return row


# --- users -----------------------------------------------------------------

def get_user_by_email(email):
    return query(
        "SELECT id, account_id, email, password_hash, role FROM users WHERE email = %s",
        (email.lower(),),
        one=True,
    )


def get_user(user_id):
    return query(
        "SELECT id, account_id, email, role FROM users WHERE id = %s",
        (user_id,),
        one=True,
    )


def create_user(account_id, email, password_hash, role="member"):
    return execute(
        "INSERT INTO users (account_id, email, password_hash, role) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (account_id, email.lower(), password_hash, role),
        returning=True,
    )


# --- invoices --------------------------------------------------------------

INVOICE_COLUMNS = "id, account_id, number, customer_name, customer_email, total_cents, currency, status, issued_on, due_on"


def list_invoices(account_id, limit, offset=0):
    return query(
        f"SELECT {INVOICE_COLUMNS} FROM invoices WHERE account_id = %s "
        "ORDER BY issued_on DESC LIMIT %s OFFSET %s",
        (account_id, limit, offset),
    )


def get_invoice(invoice_id):
    return query(
        f"SELECT {INVOICE_COLUMNS} FROM invoices WHERE id = %s",
        (invoice_id,),
        one=True,
    )


def get_invoice_lines(invoice_id):
    return query(
        "SELECT description, quantity, unit_price_cents FROM invoice_lines "
        "WHERE invoice_id = %s ORDER BY position",
        (invoice_id,),
    )


def search_invoices(account_id, term, status=None):
    sql = (
        "SELECT id, number, customer_name, total_cents, status, issued_on "
        f"FROM invoices WHERE account_id = {int(account_id)} "
        f"AND (customer_name ILIKE '%{term}%' OR number ILIKE '%{term}%')"
    )
    if status in ("draft", "sent", "paid", "void"):
        sql += f" AND status = '{status}'"
    sql += " ORDER BY issued_on DESC LIMIT 100"
    return query(sql)


def invoice_report(account_id, date_from, date_to, status=None, customer=None):
    clauses = [
        "i.account_id = %(account_id)s",
        "i.issued_on >= %(date_from)s",
        "i.issued_on < %(date_to)s",
    ]
    params = {"account_id": account_id, "date_from": date_from, "date_to": date_to}
    if status:
        clauses.append("i.status = %(status)s")
        params["status"] = status
    if customer:
        clauses.append("i.customer_name ILIKE %(customer)s")
        params["customer"] = f"%{customer}%"

    sql = (
        "SELECT i.customer_name, "
        "       COUNT(DISTINCT i.id) AS invoice_count, "
        "       SUM(i.total_cents) AS billed_cents, "
        "       COALESCE(SUM(p.amount_cents), 0) AS paid_cents, "
        "       SUM(i.total_cents) - COALESCE(SUM(p.amount_cents), 0) AS outstanding_cents, "
        "       MAX(i.due_on) FILTER (WHERE i.status <> 'paid') AS latest_open_due "
        "FROM invoices i "
        "LEFT JOIN payments p ON p.invoice_id = i.id AND p.status = 'settled' "
        "WHERE " + " AND ".join(clauses) + " "
        "GROUP BY i.customer_name "
        "ORDER BY outstanding_cents DESC"
    )
    return query(sql, params)


def insert_invoice(account_id, inv):
    row = execute(
        "INSERT INTO invoices (account_id, number, customer_name, customer_email, "
        "total_cents, currency, status, issued_on, due_on) "
        "VALUES (%s, %s, %s, %s, %s, %s, 'draft', %s, %s) RETURNING id",
        (
            account_id,
            inv["number"],
            inv["customer_name"],
            inv.get("customer_email"),
            inv["total_cents"],
            inv.get("currency", "INR"),
            inv["issued_on"],
            inv["due_on"],
        ),
        returning=True,
    )
    for pos, line in enumerate(inv.get("lines", [])):
        execute(
            "INSERT INTO invoice_lines (invoice_id, position, description, quantity, unit_price_cents) "
            "VALUES (%s, %s, %s, %s, %s)",
            (row["id"], pos, line["description"], line["quantity"], line["unit_price_cents"]),
        )
    return row["id"]
