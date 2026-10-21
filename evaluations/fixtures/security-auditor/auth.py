import functools
import hashlib

from flask import g, jsonify, session

import db


def hash_password(password):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash


def authenticate(email, password):
    user = db.get_user_by_email(email)
    if user is None or not verify_password(password, user["password_hash"]):
        return None
    return user


def login_user(user):
    session.clear()
    session["user_id"] = user["id"]
    session.permanent = True


def logout_user():
    session.clear()


def load_current_user():
    user_id = session.get("user_id")
    g.user = db.get_user(user_id) if user_id else None


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            return jsonify(error="authentication required"), 401
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @functools.wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.user["role"] != "admin":
            return jsonify(error="forbidden"), 403
        return view(*args, **kwargs)

    return wrapped
