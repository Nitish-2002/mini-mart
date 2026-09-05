"""AUTH's outbound email — OTP codes and Admin's recovery link, the only two
things AUTH ever emails (solution.md's Integration Intent: AUTH is the only
module that talks to EMAIL_PROVIDER for these; ORDERS' own notification
emails are separate and not routed through AUTH).

Fire-and-forget, no delivery-confirmation loop (trd.md §6a): a send failure
is logged, never raised — the OTP/reset-token row already exists regardless,
and the user's own resend action is the retry mechanism, not this client.
"""

import json
import logging
import os

import resend

from app.auth.config import auth_settings

logger = logging.getLogger(__name__)

resend.api_key = auth_settings.resend_api_key

_FROM_ADDRESS = "Mini Mart <noreply@minimart.app>"

# TASK-AUTH-018/019's own need, not a production code path: Playwright's E2E
# suite runs the backend as a separate real process it can't monkeypatch
# (unlike pytest's fake_email fixture in the same process) but still needs
# to read a real OTP code/reset link. When set, every send is appended as a
# JSON line to this file instead of calling Resend; unset (every real
# environment) leaves this branch dead code.
_OUTBOX_FILE = os.environ.get("EMAIL_OUTBOX_FILE")


def _deliver(payload: dict) -> None:
    if _OUTBOX_FILE:
        with open(_OUTBOX_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        return
    resend.Emails.send(payload)


def send_otp_email(to_email: str, code: str) -> None:
    """TRD-AUTH-012 / inv-auth-no-secrets-in-logs: never log the code itself."""
    try:
        _deliver(
            {
                "from": _FROM_ADDRESS,
                "to": [to_email],
                "subject": "Your Mini Mart verification code",
                "text": f"Your verification code is {code}. It expires in 10 minutes.",
            }
        )
    except Exception:
        logger.warning("OTP email send failed for %s", to_email, exc_info=True)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    try:
        _deliver(
            {
                "from": _FROM_ADDRESS,
                "to": [to_email],
                "subject": "Reset your Mini Mart admin password",
                "text": f"Reset your password: {reset_link}\n\nIf you didn't request this, ignore this email.",
            }
        )
    except Exception:
        logger.warning("Password reset email send failed for %s", to_email, exc_info=True)
