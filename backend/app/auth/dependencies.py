"""get_current_user() / require_role() — the in-process authorization
contract every protected route in every module calls (system-architecture.md
Backend Architecture; decision-76, trd.md). CATALOG and ORDERS import these
same functions by name once their own modules exist; the signature here is a
cross-module contract, not an AUTH-internal detail.
"""

import uuid
from dataclasses import dataclass

import jwt
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_settings
from app.auth.crypto import hash_jti
from app.auth.models import AuthDeliveryAgent, AuthSession
from app.auth.session import COOKIE_NAME, JWT_ALGORITHM
from app.core.db import get_session


@dataclass(frozen=True)
class Principal:
    user_id: uuid.UUID
    role: str
    jti: str


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> Principal:
    """TRD-AUTH-004 / SY-AUTH-013: a missing cookie, an invalid/expired JWT,
    and a validly-signed-but-revoked jti are all rejected identically (401) —
    system.md's Failure Shape deliberately doesn't let a caller distinguish
    "never logged in" from "session ran out" or "was revoked".
    """
    if session_token is None:
        raise HTTPException(status_code=401, detail={"error": "unauthorized"})

    try:
        claims = jwt.decode(
            session_token, auth_settings.jwt_signing_secret, algorithms=[JWT_ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={"error": "unauthorized"}) from None

    # decision-71: the signature+exp check above is cryptographic, no DB: this
    # is the one indexed lookup that catches an explicit revocation (logout).
    stmt = select(AuthSession).where(AuthSession.jti_hash == hash_jti(claims["jti"]))
    session_row = (await session.execute(stmt)).scalar_one_or_none()
    if session_row is None or session_row.revoked_at is not None:
        raise HTTPException(status_code=401, detail={"error": "unauthorized"})

    return Principal(user_id=uuid.UUID(claims["sub"]), role=claims["role"], jti=claims["jti"])


def require_role(role: str):
    """A valid session with the wrong role is rejected distinctly (403) from
    no/invalid/revoked session (401) — the one case system.md's Failure Shape
    *does* let a caller tell apart, since it's what lets a frontend redirect
    to the correct login screen instead of a generic error.
    """

    async def dependency(principal: Principal = Depends(get_current_user)) -> Principal:
        if principal.role != role:
            raise HTTPException(status_code=403, detail={"error": "forbidden"})
        return principal

    return dependency


async def require_approved_agent(
    principal: Principal = Depends(require_role("delivery_agent")),
    session: AsyncSession = Depends(get_session),
) -> Principal:
    """SY-AUTH-014: an agent-only action is rejected even with a valid,
    unexpired session if the agent's current status isn't `approved` — a
    `deactivated` agent's existing session is NOT revoked (decision-54,
    solution.md leaves it be), so this check, not session validity, is what
    actually blocks them from new assignments.
    """
    agent = (
        await session.execute(
            select(AuthDeliveryAgent).where(AuthDeliveryAgent.id == principal.user_id)
        )
    ).scalar_one_or_none()
    if agent is None or agent.status != "approved":
        raise HTTPException(status_code=403, detail={"error": "forbidden"})
    return principal
