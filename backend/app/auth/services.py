"""Business logic for AUTH's identity, agent-lifecycle, and admin-login
flows, plus the get_current_user()/require_role() authorization dependency
(TASK-AUTH-012) that CATALOG and ORDERS will import once their own modules
exist.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crypto, email
from app.auth.models import AuthOtpCode

# decision-28 (business-requirements.md)
OTP_EXPIRY = timedelta(minutes=10)
OTP_RESEND_COOLDOWN_SECONDS = 60
# decision-53 (solution.md)
OTP_RATE_LIMIT_PER_HOUR = 5
OTP_RATE_LIMIT_WINDOW = timedelta(hours=1)


class RateLimitExceeded(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds


@dataclass(frozen=True)
class OtpRequestResult:
    cooldown_seconds: int
    expires_in_seconds: int


async def request_otp(session: AsyncSession, otp_email: str, role: str) -> OtpRequestResult:
    """TRD-AUTH-005: enforces the 5/hour rate limit via a Postgres COUNT,
    indexed on (email, role, issued_at) per trd.md §5a. TRD-AUTH-007: does
    NOT mutate any prior row — auth_otp_codes has no dedupe key by design
    (trd.md §5a); supersession happens because otp_verify only ever reads
    the single latest row for (email, role), never an older one.
    """
    now = datetime.now(timezone.utc)
    window_start = now - OTP_RATE_LIMIT_WINDOW

    count_stmt = select(func.count()).where(
        AuthOtpCode.email == otp_email,
        AuthOtpCode.role == role,
        AuthOtpCode.issued_at > window_start,
    )
    count = (await session.execute(count_stmt)).scalar_one()
    if count >= OTP_RATE_LIMIT_PER_HOUR:
        # Retry-after is measured from the oldest request still inside the
        # window, not a flat window length — the limit rolls, it doesn't reset.
        oldest_stmt = (
            select(AuthOtpCode.issued_at)
            .where(
                AuthOtpCode.email == otp_email,
                AuthOtpCode.role == role,
                AuthOtpCode.issued_at > window_start,
            )
            .order_by(AuthOtpCode.issued_at.asc())
            .limit(1)
        )
        oldest_issued_at = (await session.execute(oldest_stmt)).scalar_one()
        retry_after = oldest_issued_at + OTP_RATE_LIMIT_WINDOW - now
        raise RateLimitExceeded(retry_after_seconds=max(1, int(retry_after.total_seconds())))

    code = crypto.generate_otp_code()
    otp_row = AuthOtpCode(
        email=otp_email,
        role=role,
        code_hash=crypto.hash_otp_code(code),
        expires_at=now + OTP_EXPIRY,
    )
    session.add(otp_row)
    await session.commit()

    # Fire-and-forget (trd.md §6a) — a send failure never blocks the 202.
    email.send_otp_email(otp_email, code)

    return OtpRequestResult(
        cooldown_seconds=OTP_RESEND_COOLDOWN_SECONDS,
        expires_in_seconds=int(OTP_EXPIRY.total_seconds()),
    )
