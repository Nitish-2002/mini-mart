"""Business logic for AUTH's identity, agent-lifecycle, and admin-login
flows, plus the get_current_user()/require_role() authorization dependency
(TASK-AUTH-012) that CATALOG and ORDERS will import once their own modules
exist.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crypto, email, session as session_module
from app.auth.models import AuthDeliveryAgent, AuthEndUser, AuthOtpCode

# decision-28 (business-requirements.md)
OTP_EXPIRY = timedelta(minutes=10)
OTP_RESEND_COOLDOWN_SECONDS = 60
# decision-53 (solution.md)
OTP_RATE_LIMIT_PER_HOUR = 5
OTP_RATE_LIMIT_WINDOW = timedelta(hours=1)


class RateLimitExceeded(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds


class InvalidCode(Exception):
    """Also used when a delivery_agent verify targets an email with no
    existing AuthDeliveryAgent row — deliberately the same shape as a wrong
    code, so this endpoint never reveals whether an email is a registered
    agent (the same enumeration-resistance pattern trd.md's Failure Shape
    and decision-77 already established elsewhere in this module).
    """


class CodeExpired(Exception):
    pass


class EmailAlreadyRegistered(Exception):
    pass


@dataclass(frozen=True)
class OtpRequestResult:
    cooldown_seconds: int
    expires_in_seconds: int


@dataclass(frozen=True)
class OtpVerifyResult:
    session_token: str
    role: str
    expires_at: datetime


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


async def verify_otp(session: AsyncSession, otp_email: str, code: str, role: str) -> OtpVerifyResult:
    """TRD-AUTH-009: a wrong code never sets consumed_at — the row stays
    valid for a further attempt until it expires or is correctly entered.
    Only the single latest row for (email, role) is ever checked
    (supersession, per TASK-AUTH-006's own note).
    """
    stmt = (
        select(AuthOtpCode)
        .where(AuthOtpCode.email == otp_email, AuthOtpCode.role == role)
        .order_by(AuthOtpCode.issued_at.desc())
        .limit(1)
    )
    otp_row = (await session.execute(stmt)).scalar_one_or_none()

    if otp_row is None or otp_row.consumed_at is not None:
        raise InvalidCode()

    now = datetime.now(timezone.utc)
    if otp_row.expires_at < now:
        raise CodeExpired()

    if not crypto.verify_otp_code(code, otp_row.code_hash):
        raise InvalidCode()

    if role == "end_user":
        identity_id = await _get_or_create_end_user_id(session, otp_email)
    else:
        identity_id = await _get_delivery_agent_id(session, otp_email)
        if identity_id is None:
            # No registration exists for this email under this role — same
            # response shape as a wrong code, see InvalidCode's own docstring.
            raise InvalidCode()

    otp_row.consumed_at = now
    issued = await session_module.issue_session(session, role, identity_id)
    await session.commit()

    return OtpVerifyResult(
        session_token=issued.token, role=role, expires_at=issued.expires_at
    )


async def _get_or_create_end_user_id(session: AsyncSession, otp_email: str):
    existing = (
        await session.execute(select(AuthEndUser).where(AuthEndUser.email == otp_email))
    ).scalar_one_or_none()
    if existing is not None:
        return existing.id
    new_user = AuthEndUser(email=otp_email)
    session.add(new_user)
    await session.flush()  # populate new_user.id without committing yet
    return new_user.id


async def _get_delivery_agent_id(session: AsyncSession, otp_email: str):
    agent = (
        await session.execute(
            select(AuthDeliveryAgent).where(AuthDeliveryAgent.email == otp_email)
        )
    ).scalar_one_or_none()
    return agent.id if agent is not None else None


async def register_agent(session: AsyncSession, name: str, phone: str, agent_email: str, photo_url: str) -> None:
    """TRD-AUTH-014: relies on auth_delivery_agents.email's DB-level UNIQUE
    constraint (trd.md §5a) rather than a check-then-insert, so a race
    between two concurrent registrations for the same email can't slip
    through — the second one always loses to the constraint, not a timing
    window. photo_url is accepted as-is: this endpoint never touches
    OBJECT_STORAGE itself, only stores the URL the frontend already uploaded to.
    """
    agent = AuthDeliveryAgent(name=name, phone=phone, email=agent_email, photo_url=photo_url)
    session.add(agent)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise EmailAlreadyRegistered() from None
