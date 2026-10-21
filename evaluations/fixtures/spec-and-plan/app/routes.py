"""HTTP routes (Flask). Auth via session cookie; see auth.py."""
from flask import Blueprint, abort, g, jsonify, redirect, render_template, request, url_for

from .auth import login_required, require_role
from .db import session
from .emails import send_welcome_email
from .models import Membership, Role, User, Workspace

bp = Blueprint("app", __name__)


@bp.post("/signup")
def signup():
    email = request.form["email"].strip().lower()
    if session.query(User).filter_by(email=email).first():
        return render_template("signup.html", error="Email already registered"), 400
    user = User(email=email, name=request.form.get("name"))
    user.set_password(request.form["password"])
    session.add(user)
    session.commit()
    send_welcome_email(user)
    return redirect(url_for("app.onboarding"))


@bp.get("/w/<slug>/members")
@login_required
@require_role(Role.OWNER, Role.ADMIN, Role.MEMBER, Role.VIEWER)
def members_page(slug):
    ws = session.query(Workspace).filter_by(slug=slug).first_or_404()
    return render_template("members.html", workspace=ws, memberships=ws.memberships)


@bp.post("/admin/w/<slug>/members")
@login_required
@require_role(Role.OWNER, Role.ADMIN)
def add_member_by_id(slug):
    """Current way to add a teammate: owner/admin pastes an existing user ID."""
    ws = session.query(Workspace).filter_by(slug=slug).first_or_404()
    user = session.get(User, int(request.form["user_id"])) or abort(404)
    role = Role(request.form.get("role", "member"))
    session.add(Membership(user=user, workspace=ws, role=role))
    session.commit()
    return redirect(url_for("app.members_page", slug=slug))


@bp.delete("/api/w/<slug>/members/<int:membership_id>")
@login_required
@require_role(Role.OWNER, Role.ADMIN)
def remove_member(slug, membership_id):
    m = session.get(Membership, membership_id) or abort(404)
    if m.workspace.slug != slug or m.role == Role.OWNER:
        abort(403)
    session.delete(m)
    session.commit()
    return jsonify(ok=True)
