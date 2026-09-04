"""TASK-AUTH-020: Security hardening test suite — hashing round-trips,
JWT round-trip, validators, the admin-singleton constraint, the
no-secrets-in-logs assertion, and the per-IP admin-login rate limiter.
One test function per TEST-AUTH-NNN id, per test-specification.md's Unit
Tests and Edge/Failure/Security/Performance/and Recovery Tests tables.

TEST-AUTH-003 (constant-time comparison) is deliberately NOT here — per its
own row in test-specification.md, it's a manual code-review checklist item
(see .github/pull_request_template.md), not a runtime test.
"""

import logging
import re
import uuid

import jwt
import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.auth import crypto
from app.auth.models import AuthAdminAccount
from app.auth.schemas import AdminPasswordResetConfirmIn, OtpRequestIn
from app.core.db import async_session_factory


def test_password_hash_roundtrip_TEST_AUTH_001():
    password = "a-representative-12char-plus-password"
    hashed = crypto.hash_password(password)

    assert hashed != password  # never stores the plaintext
    assert crypto.verify_password(password, hashed) is True
    assert crypto.verify_password("a-completely-different-password", hashed) is False


def test_keyed_hash_roundtrip_TEST_AUTH_002():
    code = "482913"
    token = crypto.generate_reset_token()

    code_hash = crypto.hash_otp_code(code)
    assert crypto.verify_otp_code(code, code_hash) is True
    assert crypto.verify_otp_code("000000", code_hash) is False

    token_hash = crypto.hash_reset_token(token)
    assert crypto.verify_reset_token(token, token_hash) is True
    assert crypto.verify_reset_token("not-the-token", token_hash) is False


def test_jwt_roundtrip_TEST_AUTH_004():
    claims = {"sub": "11111111-1111-1111-1111-111111111111", "role": "admin", "jti": "a-jti-value"}
    secret = "a-test-signing-secret-at-least-32-bytes-long"

    token = jwt.encode(claims, secret, algorithm="HS256")
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded == claims

    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "a-different-secret-entirely-32-bytes-long", algorithms=["HS256"])


def test_password_length_validator_TEST_AUTH_005():
    with pytest.raises(ValidationError):
        AdminPasswordResetConfirmIn(token="t", new_password="a" * 11)

    valid = AdminPasswordResetConfirmIn(token="t", new_password="a" * 12)
    assert valid.new_password == "a" * 12


def test_otp_request_role_required_TEST_AUTH_006():
    with pytest.raises(ValidationError) as exc_info:
        OtpRequestIn(email="a@example.com")  # role omitted (CR-002)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("role",) and e["type"] == "missing" for e in errors)


async def test_admin_singleton_check_constraint_TEST_AUTH_014(seeded_admin):
    async with async_session_factory() as session:
        session.add(
            AuthAdminAccount(
                id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
                username="a_second_admin",
                password_hash=crypto.hash_password("irrelevant-but-valid-password"),
                recovery_email="second@example.com",
            )
        )
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_no_secrets_in_logs_TEST_AUTH_038(
    client: AsyncClient, seeded_admin, fake_email, caplog: pytest.LogCaptureFixture
):
    caplog.set_level(logging.DEBUG)
    username, password, recovery_email = seeded_admin

    # Full OTP request/verify cycle.
    await client.post("/v1/auth/otp/request", json={"email": "otp-user@example.com", "role": "end_user"})
    otp_text = fake_email[-1]["text"]
    otp_code = re.search(r"verification code is (\d{6})", otp_text).group(1)
    await client.post(
        "/v1/auth/otp/verify",
        json={"email": "otp-user@example.com", "code": otp_code, "role": "end_user"},
    )

    # Full admin login/reset cycle.
    await client.post("/v1/auth/admin/login", json={"username": username, "password": password})
    await client.post("/v1/auth/admin/password-reset/request", json={"email": recovery_email})
    reset_text = fake_email[-1]["text"]
    reset_token = re.search(r"token=(\S+)", reset_text).group(1)
    await client.post(
        "/v1/auth/admin/password-reset/confirm",
        json={"token": reset_token, "new_password": "a-brand-new-password-1234"},
    )

    log_text = caplog.text
    assert otp_code not in log_text  # inv-auth-no-secrets-in-logs
    assert password not in log_text
    assert reset_token not in log_text
    assert "a-brand-new-password-1234" not in log_text


async def test_admin_login_rate_limit_is_per_ip_TEST_AUTH_042(seeded_admin, client_from_ip):
    username, _, _ = seeded_admin
    ip1 = client_from_ip("10.0.0.1")
    ip2 = client_from_ip("10.0.0.2")
    async with ip1, ip2:
        # 10/15min (decision-73): 10 wrong-password attempts from ip1 all get
        # through as 401; the 11th is the first to trip 429.
        for _ in range(10):
            r = await ip1.post("/v1/auth/admin/login", json={"username": username, "password": "wrong"})
            assert r.status_code == 401
        limited = await ip1.post("/v1/auth/admin/login", json={"username": username, "password": "wrong"})
        assert limited.status_code == 429

        # ip2's own first attempt is unaffected by ip1's count — it fails or
        # succeeds on its own merits (wrong password here), not on 429.
        unaffected = await ip2.post("/v1/auth/admin/login", json={"username": username, "password": "wrong"})
        assert unaffected.status_code == 401
