"""TASK-AUTH-017: Contract test suite — validates all 9 endpoints against
trd.md's API Contracts exactly (status codes, field names, field shapes),
not just the happy path. One test function per TEST-AUTH-NNN id, per
test-specification.md's Interface and Contract Tests table.
"""

import re
from datetime import datetime, timedelta, timezone

from httpx import AsyncClient

from app.auth.models import AuthOtpCode, AuthResetToken
from app.core.db import async_session_factory
from sqlalchemy import select, update


def _extract_code(email_text: str) -> str:
    match = re.search(r"verification code is (\d{6})", email_text)
    assert match, f"no OTP code found in captured email: {email_text!r}"
    return match.group(1)


def _extract_token(email_text: str) -> str:
    match = re.search(r"token=(\S+)", email_text)
    assert match, f"no reset token found in captured email: {email_text!r}"
    return match.group(1)


async def test_otp_request_TEST_AUTH_022(client: AsyncClient, fake_email):
    resp = await client.post("/v1/auth/otp/request", json={"email": "a@example.com", "role": "end_user"})
    assert resp.status_code == 202
    body = resp.json()
    assert set(body.keys()) == {"cooldown_seconds", "expires_in_seconds"}
    assert isinstance(body["cooldown_seconds"], int)
    assert isinstance(body["expires_in_seconds"], int)

    # 5/hour is the limit (decision-53) — the 6th in the window is rate_limited.
    for _ in range(4):
        r = await client.post("/v1/auth/otp/request", json={"email": "a@example.com", "role": "end_user"})
        assert r.status_code == 202
    limited = await client.post("/v1/auth/otp/request", json={"email": "a@example.com", "role": "end_user"})
    assert limited.status_code == 429
    limited_body = limited.json()
    assert limited_body["error"] == "rate_limited"
    assert isinstance(limited_body["retry_after_seconds"], int)


async def test_otp_verify_TEST_AUTH_023(client: AsyncClient, fake_email):
    await client.post("/v1/auth/otp/request", json={"email": "b@example.com", "role": "end_user"})
    code = _extract_code(fake_email[-1]["text"])

    # correct code -> 200
    ok = await client.post(
        "/v1/auth/otp/verify", json={"email": "b@example.com", "code": code, "role": "end_user"}
    )
    assert ok.status_code == 200
    ok_body = ok.json()
    assert set(ok_body.keys()) == {"role", "expires_at"}
    assert ok_body["role"] == "end_user"
    assert "session_token" not in ok.text  # CR-004: cookie only, never in the body
    assert "session_token" in ok.cookies

    # wrong code -> 401 (row not yet consumed by the correct attempt above happened already,
    # so request a fresh one to test a genuine wrong-code case)
    await client.post("/v1/auth/otp/request", json={"email": "c@example.com", "role": "end_user"})
    wrong = await client.post(
        "/v1/auth/otp/verify", json={"email": "c@example.com", "code": "000000", "role": "end_user"}
    )
    assert wrong.status_code == 401
    assert wrong.json() == {"error": "invalid_code"}

    # expired code -> 410 (force expires_at into the past directly, no 10-minute wait)
    await client.post("/v1/auth/otp/request", json={"email": "d@example.com", "role": "end_user"})
    async with async_session_factory() as session:
        await session.execute(
            update(AuthOtpCode)
            .where(AuthOtpCode.email == "d@example.com")
            .values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
        )
        await session.commit()
    code_d = _extract_code(fake_email[-1]["text"])
    expired = await client.post(
        "/v1/auth/otp/verify", json={"email": "d@example.com", "code": code_d, "role": "end_user"}
    )
    assert expired.status_code == 410
    assert expired.json() == {"error": "code_expired"}


async def test_agent_register_TEST_AUTH_024(client: AsyncClient):
    body = {"name": "Ada Agent", "phone": "+15551234567", "email": "agent@example.com", "photo_url": "https://example.com/a.jpg"}
    created = await client.post("/v1/auth/agent/register", json=body)
    assert created.status_code == 201
    assert created.json() == {"status": "pending_approval"}

    dup = await client.post("/v1/auth/agent/register", json=body)
    assert dup.status_code == 409
    assert dup.json() == {"error": "email_already_registered"}


async def test_agent_status_TEST_AUTH_025(client: AsyncClient, fake_email):
    unauth = await client.get("/v1/auth/agent/status")
    assert unauth.status_code == 401
    assert unauth.json() == {"error": "unauthorized"}

    await client.post(
        "/v1/auth/agent/register",
        json={"name": "Bo Agent", "phone": "+15550000000", "email": "bo@example.com", "photo_url": "https://example.com/b.jpg"},
    )
    await client.post("/v1/auth/otp/request", json={"email": "bo@example.com", "role": "delivery_agent"})
    code = _extract_code(fake_email[-1]["text"])
    verify = await client.post(
        "/v1/auth/otp/verify", json={"email": "bo@example.com", "code": code, "role": "delivery_agent"}
    )
    client.cookies.update(verify.cookies)

    status_resp = await client.get("/v1/auth/agent/status")
    assert status_resp.status_code == 200
    assert status_resp.json() == {"status": "pending_approval"}


async def test_admin_login_TEST_AUTH_026(client: AsyncClient, seeded_admin):
    username, password, _ = seeded_admin

    ok = await client.post("/v1/auth/admin/login", json={"username": username, "password": password})
    assert ok.status_code == 200
    assert set(ok.json().keys()) == {"expires_at"}
    assert "session_token" in ok.cookies

    bad = await client.post("/v1/auth/admin/login", json={"username": username, "password": "wrong"})
    assert bad.status_code == 401
    assert bad.json() == {"error": "invalid_credentials"}

    # 10/15min (decision-73): 2 requests already made above (ok + bad) count
    # toward the window — 8 more brings the cumulative total to exactly 10
    # (still allowed); the 11th (below) is the first to trip rate_limited.
    for _ in range(8):
        r = await client.post("/v1/auth/admin/login", json={"username": username, "password": "wrong"})
        assert r.status_code == 401
    limited = await client.post("/v1/auth/admin/login", json={"username": username, "password": "wrong"})
    assert limited.status_code == 429
    assert limited.json()["error"] == "rate_limited"


async def test_admin_password_reset_request_TEST_AUTH_027(client: AsyncClient, seeded_admin, fake_email):
    _, _, recovery_email = seeded_admin

    matching = await client.post("/v1/auth/admin/password-reset/request", json={"email": recovery_email})
    assert matching.status_code == 202
    assert matching.json() == {}

    not_matching = await client.post(
        "/v1/auth/admin/password-reset/request", json={"email": "nobody@example.com"}
    )
    assert not_matching.status_code == 202
    assert not_matching.json() == {}
    # decision-77: identical response either way — no observable difference in shape or status.


async def test_admin_password_reset_confirm_TEST_AUTH_028(client: AsyncClient, seeded_admin, fake_email):
    _, _, recovery_email = seeded_admin
    await client.post("/v1/auth/admin/password-reset/request", json={"email": recovery_email})
    token = _extract_token(fake_email[-1]["text"])

    valid = await client.post(
        "/v1/auth/admin/password-reset/confirm",
        json={"token": token, "new_password": "a-new-valid-password-123"},
    )
    assert valid.status_code == 200
    assert valid.json() == {}
    assert "session_token" in valid.cookies

    # used: the same token confirmed again is rejected (TRD-AUTH-008, single-use).
    reused = await client.post(
        "/v1/auth/admin/password-reset/confirm",
        json={"token": token, "new_password": "another-valid-password-456"},
    )
    assert reused.status_code == 410
    assert reused.json() == {"error": "token_expired_or_used"}

    # expired: a fresh token whose expires_at has already elapsed is rejected the same way.
    await client.post("/v1/auth/admin/password-reset/request", json={"email": recovery_email})
    expired_token = _extract_token(fake_email[-1]["text"])
    async with async_session_factory() as session:
        await session.execute(
            update(AuthResetToken).values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
        )
        await session.commit()
    expired = await client.post(
        "/v1/auth/admin/password-reset/confirm",
        json={"token": expired_token, "new_password": "yet-another-password-789"},
    )
    assert expired.status_code == 410
    assert expired.json() == {"error": "token_expired_or_used"}


async def test_logout_TEST_AUTH_029(client: AsyncClient, seeded_admin):
    username, password, _ = seeded_admin
    login = await client.post("/v1/auth/admin/login", json={"username": username, "password": password})
    client.cookies.update(login.cookies)

    logout = await client.post("/v1/auth/logout")
    assert logout.status_code == 204

    # the same (now-revoked) cookie is rejected on a subsequent authenticated call.
    again = await client.post("/v1/auth/logout")
    assert again.status_code == 401
