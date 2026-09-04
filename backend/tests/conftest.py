"""Shared fixtures for every AUTH test suite (TASK-AUTH-017/020/021/022).

Points the app at a real, disposable Postgres database — mini_mart_test,
owned by a dedicated low-privilege minimart_test role — rather than a mock
or SQLite substitute, so these tests exercise genuine Postgres behavior
(CITEXT case-insensitivity, native ENUM, the admin-singleton CHECK
constraint) instead of an approximation that could pass while the real
schema fails. Credentials live only in the gitignored backend/.env.test,
never in this file or any commit.

Env vars MUST be set before any `app.*` module is imported anywhere in the
process — app.core.db builds its engine from app.core.config.settings at
import time. This file is pytest's first import, so _load_env_test() runs
before the app imports below.
"""

import os
from pathlib import Path


def _load_env_test() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env.test"
    if not env_path.exists():
        raise RuntimeError(
            "backend/.env.test not found — tests need a real Postgres test "
            "database. See tests/conftest.py's own docstring for how it's set up."
        )
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os.environ[key] = value


_load_env_test()

import uuid  # noqa: E402
from collections.abc import AsyncIterator, Callable  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.auth import crypto  # noqa: E402
from app.auth.models import ADMIN_SINGLETON_ID, AuthAdminAccount  # noqa: E402
from app.core.db import Base, async_session_factory, engine  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402
from app.main import app  # noqa: E402

pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _schema() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _clean_state() -> AsyncIterator[None]:
    """Each test starts from an empty DB and a reset rate-limiter — slowapi's
    in-memory counters otherwise leak across tests in the same process.
    """
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    limiter.reset()
    yield


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    # https:// scheme, not http:// — set_session_cookie() always sets Secure
    # (CR-004's design, even for LOCAL), and httpx's cookie jar (like a real
    # browser) refuses to resend a Secure cookie over a non-https request.
    async with AsyncClient(transport=transport, base_url="https://test") as ac:
        yield ac


@pytest.fixture
def client_from_ip() -> Callable[[str], AsyncClient]:
    """A second client presenting a different remote IP — TEST-AUTH-042 needs
    two distinct addresses to prove the admin-login rate limit is per-IP.
    """

    def _make(ip: str) -> AsyncClient:
        transport = ASGITransport(app=app, client=(ip, 12345))
        return AsyncClient(transport=transport, base_url="https://test")

    return _make


ADMIN_TEST_USERNAME = "test_admin"
ADMIN_TEST_PASSWORD = "test-admin-password-not-real-12345"
ADMIN_TEST_RECOVERY_EMAIL = "test-admin@example.com"


@pytest_asyncio.fixture
async def seeded_admin() -> tuple[str, str, str]:
    """Inserts the singleton Admin row directly (mirrors what the real
    migration does with ADMIN_SEED_* env vars, TASK-AUTH-005) and returns
    (username, plaintext_password, recovery_email) for the calling test.
    """
    async with async_session_factory() as session:
        session.add(
            AuthAdminAccount(
                id=ADMIN_SINGLETON_ID,
                username=ADMIN_TEST_USERNAME,
                password_hash=crypto.hash_password(ADMIN_TEST_PASSWORD),
                recovery_email=ADMIN_TEST_RECOVERY_EMAIL,
            )
        )
        await session.commit()
    return ADMIN_TEST_USERNAME, ADMIN_TEST_PASSWORD, ADMIN_TEST_RECOVERY_EMAIL


@pytest.fixture
def fake_email(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Records every outbound send as {"to": [...], "subject": ..., "text": ...}
    instead of calling the real Resend API — every test except TASK-AUTH-021's
    TEST-AUTH-041 (real provider, PREVIEW-only) uses this double, per
    test-specification.md's own Test Data Strategy.
    """
    sent: list[dict] = []

    def _fake_send(payload: dict) -> dict:
        sent.append(payload)
        return {"id": str(uuid.uuid4())}

    monkeypatch.setattr("app.auth.email.resend.Emails.send", _fake_send)
    return sent


@pytest.fixture
def failing_email(monkeypatch: pytest.MonkeyPatch) -> None:
    """TEST-AUTH-039's fake EMAIL_PROVIDER double that always raises —
    proves the fire-and-forget design (trd.md 6a) actually swallows the
    failure rather than surfacing it to the caller.
    """

    def _raise(payload: dict):
        raise RuntimeError("simulated EMAIL_PROVIDER outage")

    monkeypatch.setattr("app.auth.email.resend.Emails.send", _raise)
