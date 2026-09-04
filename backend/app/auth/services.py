"""Business logic for AUTH's identity, agent-lifecycle, and admin-login
flows, plus the get_current_user()/require_role() authorization dependency
(TASK-AUTH-012) that CATALOG and ORDERS will import once their own modules
exist.
"""

import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crypto, email, session as session_module
from app.auth.models import (
    AuthAdminAccount,
    AuthAgentStatusLog,
    AuthDeliveryAgent,
    AuthEndUser,
    AuthOtpCode,
    AuthResetToken,
)

# sm-auth-agent-status's closed transition table (trd.md §5b) — the only
# valid (current_status, action) -> new_status moves. Anything else is
# rejected as InvalidTransition, per TASK-AUTH-009's own decision budget.
AGENT_TRANSITIONS: dict[tuple[str, str], str] = {
    ("pending_approval", "approve"): "approved",
    ("pending_approval", "reject"): "rejected",
    ("approved", "deactivate"): "deactivated",
    ("deactivated", "reactivate"): "approved",  # decision-55
}

# decision-28 (business-requirements.md)
OTP_EXPIRY = timedelta(minutes=10)
OTP_RESEND_COOLDOWN_SECONDS = 60
# decision-53 (solution.md)
OTP_RATE_LIMIT_PER_HOUR = 5
OTP_RATE_LIMIT_WINDOW = timedelta(hours=1)
# No expiry duration was ever fixed upstream for reset tokens (only OTP's
# 10 minutes is a real decision, decision-28) — 1 hour is this task's own
# implementation-time default: long enough that checking email isn't a race,
# short enough to bound a stale unused link. Not escalated: low-stakes,
# easily revised (see trd.md's own reversal-trigger pattern for this kind
# of implementation default).
RESET_TOKEN_EXPIRY = timedelta(hours=1)


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


class AgentNotFound(Exception):
    pass


class InvalidTransition(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class ResetTokenInvalid(Exception):
    pass


@dataclass(frozen=True)
class AdminLoginResult:
    session_token: str
    expires_at: datetime


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


# A precomputed hash of a value nobody will ever type, spent purely so a
# missing-username lookup pays the same Argon2 cost as a real-username wrong-
# password check — otherwise a missing username would respond measurably
# faster, leaking username existence via timing despite the identical 401
# body (system.md's Failure Shape / decision-77's enumeration-resistance
# principle, extended to a side channel the response body itself can't hide).
_DUMMY_PASSWORD_HASH = crypto.hash_password(secrets.token_urlsafe(32))


async def admin_login(session: AsyncSession, username: str, password: str) -> AdminLoginResult:
    admin = (
        await session.execute(select(AuthAdminAccount).where(AuthAdminAccount.username == username))
    ).scalar_one_or_none()

    if admin is None:
        crypto.verify_password(password, _DUMMY_PASSWORD_HASH)  # timing parity, see above
        raise InvalidCredentials()

    if not crypto.verify_password(password, admin.password_hash):
        raise InvalidCredentials()

    issued = await session_module.issue_session(session, "admin", admin.id)
    await session.commit()
    return AdminLoginResult(session_token=issued.token, expires_at=issued.expires_at)


async def request_password_reset(session: AsyncSession, recovery_email: str) -> None:
    """TRD-AUTH-010 / decision-77: always succeeds silently, whether or not
    `recovery_email` matches the singleton admin's registered address — the
    caller has no way to tell the two cases apart, by design.
    """
    admin = (
        await session.execute(
            select(AuthAdminAccount).where(AuthAdminAccount.recovery_email == recovery_email)
        )
    ).scalar_one_or_none()
    if admin is None:
        return

    token = crypto.generate_reset_token()
    now = datetime.now(timezone.utc)
    session.add(
        AuthResetToken(
            admin_account_id=admin.id,
            token_hash=crypto.hash_reset_token(token),
            expires_at=now + RESET_TOKEN_EXPIRY,
        )
    )
    await session.commit()
    email.send_password_reset_email(recovery_email, _build_reset_link(token))


async def confirm_password_reset(
    session: AsyncSession, token: str, new_password: str
) -> AdminLoginResult:
    """TRD-AUTH-008 / inv-auth-single-use-tokens: only the single latest
    auth_reset_tokens row (any admin — there's only ever one) is checked,
    same supersession pattern as OTP. Password update + used_at both commit
    in one transaction. Auto-issues a session on success (SS-AUTH-004's
    "Admin sets a new password... " outcome includes being logged in after).
    """
    stmt = select(AuthResetToken).order_by(AuthResetToken.issued_at.desc()).limit(1)
    reset_row = (await session.execute(stmt)).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if (
        reset_row is None
        or reset_row.used_at is not None
        or reset_row.expires_at < now
        or not crypto.verify_reset_token(token, reset_row.token_hash)
    ):
        raise ResetTokenInvalid()

    admin = (
        await session.execute(
            select(AuthAdminAccount).where(AuthAdminAccount.id == reset_row.admin_account_id)
        )
    ).scalar_one()

    reset_row.used_at = now
    admin.password_hash = crypto.hash_password(new_password)
    issued = await session_module.issue_session(session, "admin", admin.id)
    await session.commit()

    return AdminLoginResult(session_token=issued.token, expires_at=issued.expires_at)


def _build_reset_link(token: str) -> str:
    # URL format/routing is this task's own decision to make (decision budget).
    return f"https://admin.minimart.app/reset-password?token={token}"


async def update_agent_status(
    session: AsyncSession, agent_id: uuid.UUID, action: str, admin_id: uuid.UUID
) -> str:
    """CR-005 / TRD-AUTH-011 / inv-auth-audit-atomicity: the status update
    and the audit-log row are one transaction — a rollback anywhere here
    (e.g. the commit failing) takes both back, never just one.
    """
    agent = (
        await session.execute(select(AuthDeliveryAgent).where(AuthDeliveryAgent.id == agent_id))
    ).scalar_one_or_none()
    if agent is None:
        raise AgentNotFound()

    new_status = AGENT_TRANSITIONS.get((agent.status, action))
    if new_status is None:
        raise InvalidTransition()

    old_status = agent.status
    agent.status = new_status
    session.add(
        AuthAgentStatusLog(
            agent_id=agent_id, old_status=old_status, new_status=new_status, changed_by=admin_id
        )
    )
    await session.commit()
    return new_status
