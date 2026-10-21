"""Transactional email. Sent synchronously through Postmark in the request."""
from flask import render_template

from .postmark_client import postmark

FROM_ADDRESS = "Fieldnote <hello@fieldnote.app>"


def _send(to: str, subject: str, template: str, **ctx) -> None:
    postmark.send(
        From=FROM_ADDRESS,
        To=to,
        Subject=subject,
        HtmlBody=render_template(f"emails/{template}.html", **ctx),
    )


def send_welcome_email(user) -> None:
    _send(user.email, "Welcome to Fieldnote", "welcome", user=user)


def send_password_reset(user, token: str) -> None:
    _send(user.email, "Reset your Fieldnote password", "password_reset", user=user, token=token)
