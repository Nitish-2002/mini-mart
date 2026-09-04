"""Session issuance — the one mechanism both OTP verify (TASK-AUTH-007) and
Admin login (TASK-AUTH-010) share, so the JWT shape is defined exactly once.
Verification/revocation (get_current_user()/require_role()) is
TASK-AUTH-012 — this module only issues.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_settings
from app.auth.crypto import hash_jti
from app.auth.models import AuthSession

# decision-52 (solution.md) — same lifetime for every role.
SESSION_LIFETIME = timedelta(days=7)
JWT_ALGORITHM = "HS256"  # decision-70 (trd.md)


@dataclass(frozen=True)
class IssuedSession:
    token: str
    expires_at: datetime


async def issue_session(db_session: AsyncSession, role: str, user_id: uuid.UUID) -> IssuedSession:
    """Adds the new auth_sessions row to `db_session` without committing —
    callers that need the session issuance atomic with another write (e.g.
    OTP verify's consumed_at update) commit once, together.
    """
    now = datetime.now(timezone.utc)
    expires_at = now + SESSION_LIFETIME
    jti = str(uuid.uuid4())

    token = jwt.encode(
        {"sub": str(user_id), "role": role, "jti": jti, "iat": now, "exp": expires_at},
        auth_settings.jwt_signing_secret,
        algorithm=JWT_ALGORITHM,
    )

    db_session.add(
        AuthSession(jti_hash=hash_jti(jti), role=role, user_id=user_id, expires_at=expires_at)
    )

    return IssuedSession(token=token, expires_at=expires_at)
