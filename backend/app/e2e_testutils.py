"""Test-only reset endpoint for TASK-AUTH-018/019's Playwright suite.

Registered in app/main.py ONLY when E2E_TEST_MODE is set — never present in
any real environment. Playwright's own process can't reach into this
backend's Python process the way pytest's fixtures do (separate OS
processes), so it needs an HTTP-callable way to get back to a clean,
reseeded state between journeys — the same thing tests/conftest.py's
_clean_state fixture does in-process for the pytest suite.
"""

import os

from argon2 import PasswordHasher
from fastapi import APIRouter

from app.auth.models import ADMIN_SINGLETON_ID, AuthAdminAccount
from app.core.db import Base, async_session_factory, engine

router = APIRouter(prefix="/_test", tags=["test-only"])


@router.post("/reset")
async def reset_e2e_state() -> dict:
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    async with async_session_factory() as session:
        session.add(
            AuthAdminAccount(
                id=ADMIN_SINGLETON_ID,
                username=os.environ.get("ADMIN_SEED_USERNAME", "e2e_admin"),
                password_hash=PasswordHasher().hash(
                    os.environ.get("ADMIN_SEED_PASSWORD", "e2e-admin-password-not-real-12345678")
                ),
                recovery_email=os.environ.get("ADMIN_SEED_EMAIL", "e2e-admin@example.com"),
            )
        )
        await session.commit()

    outbox_file = os.environ.get("EMAIL_OUTBOX_FILE")
    if outbox_file and os.path.exists(outbox_file):
        open(outbox_file, "w").close()

    return {"status": "reset"}
