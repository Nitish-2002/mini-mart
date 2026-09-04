"""AUTH's outbound email — OTP codes and Admin's recovery link, the only two
things AUTH ever emails (solution.md's Integration Intent: AUTH is the only
module that talks to EMAIL_PROVIDER for these; ORDERS' own notification
emails are separate and not routed through AUTH).

Fire-and-forget, no delivery-confirmation loop (trd.md §6a): a send failure
is logged, never raised — the OTP/reset-token row already exists regardless,
and the user's own resend action is the retry mechanism, not this client.
"""

import logging

import resend

from app.auth.config import auth_settings

logger = logging.getLogger(__name__)

resend.api_key = auth_settings.resend_api_key

_FROM_ADDRESS = "Mini Mart <noreply@minimart.app>"


def send_otp_email(to_email: str, code: str) -> None:
    """TRD-AUTH-012 / inv-auth-no-secrets-in-logs: never log the code itself."""
    try:
        resend.Emails.send(
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
        resend.Emails.send(
            {
                "from": _FROM_ADDRESS,
                "to": [to_email],
                "subject": "Reset your Mini Mart admin password",
                "text": f"Reset your password: {reset_link}\n\nIf you didn't request this, ignore this email.",
            }
        )
    except Exception:
        logger.warning("Password reset email send failed for %s", to_email, exc_info=True)
