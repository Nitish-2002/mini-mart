"""Hashing/comparison primitives shared by every AUTH flow that touches a
secret: OTP codes, reset tokens (keyed HMAC-SHA256, decision-69), and the
Admin password (Argon2id, decision-68 — added in TASK-AUTH-010). All secret
comparisons use constant-time equality (TRD-AUTH-015) — never `==`.
"""

import hashlib
import hmac
import secrets

from app.auth.config import auth_settings


def generate_otp_code() -> str:
    """A cryptographically random 6-digit code, zero-padded."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp_code(code: str) -> str:
    return _keyed_hash(code)


def verify_otp_code(code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hash_otp_code(code), code_hash)


def generate_reset_token() -> str:
    """A high-entropy, URL-safe token — no need to be human-enterable."""
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return _keyed_hash(token)


def verify_reset_token(token: str, token_hash: str) -> bool:
    return hmac.compare_digest(hash_reset_token(token), token_hash)


def _keyed_hash(value: str) -> str:
    """HMAC-SHA256, keyed by the server-only OTP_HMAC_PEPPER (decision-69) —
    fast (appropriate for already-high-entropy or rate-limited secrets) but
    still resistant to offline brute-force from a database-only leak, since
    the pepper never leaves the environment.
    """
    return hmac.new(
        auth_settings.otp_hmac_pepper.encode(), value.encode(), hashlib.sha256
    ).hexdigest()
