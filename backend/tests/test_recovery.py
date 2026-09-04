"""TASK-AUTH-022: Recovery/failure-mode test — proves the fire-and-forget
EMAIL_PROVIDER design (trd.md 6a, risk-auth-email-outage) actually holds:
a send failure never blocks OTP issuance or surfaces to the caller.
"""

from sqlalchemy import select

from app.auth.models import AuthOtpCode
from app.core.db import async_session_factory


async def test_otp_request_survives_email_outage_TEST_AUTH_039(client, failing_email):
    resp = await client.post(
        "/v1/auth/otp/request", json={"email": "outage-user@example.com", "role": "end_user"}
    )

    # No exception surfaces to the caller — still a normal 202 with the
    # documented body shape, even though the email double raised.
    assert resp.status_code == 202
    body = resp.json()
    assert set(body.keys()) == {"cooldown_seconds", "expires_in_seconds"}

    # The auth_otp_codes row exists regardless — it would validate if the
    # user somehow learned the code via a support channel.
    async with async_session_factory() as session:
        row = (
            await session.execute(
                select(AuthOtpCode).where(AuthOtpCode.email == "outage-user@example.com")
            )
        ).scalar_one_or_none()
    assert row is not None
    assert row.consumed_at is None
