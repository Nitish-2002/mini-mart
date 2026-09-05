"""auth foundation tables

Revision ID: 898ac5d5fcb5
Revises:
Create Date: 2026-09-04 15:09:32.088932

Implements trd.md's Data Model / DDL exactly (TASK-AUTH-005) — all 7 auth_*
tables, plus the auth_admin_accounts singleton seed row. The seed identity
(username/email/password) is read from environment variables at migration
run time, never hardcoded — this repo is public, so no real personal data
or credential belongs in git history. Unset vars fall back to obviously-fake
local-dev placeholders, matching the pattern in app/auth/config.py.
"""
import os
import uuid
from typing import Sequence, Union

from alembic import op
from argon2 import PasswordHasher
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '898ac5d5fcb5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ADMIN_SINGLETON_ID = "00000000-0000-0000-0000-000000000001"
ADMIN_SEED_USERNAME = os.environ.get("ADMIN_SEED_USERNAME", "admin")
ADMIN_SEED_EMAIL = os.environ.get("ADMIN_SEED_EMAIL", "admin@example.com")
ADMIN_SEED_PASSWORD = os.environ.get("ADMIN_SEED_PASSWORD", "local-dev-insecure-default-changeme")

# create_type=False: the type is created exactly once below via raw SQL,
# matching the DDL's own "CREATE TYPE once, reference it in two CREATE TABLEs"
# shape. Without this, create_table() would try to CREATE TYPE a second time
# for auth_agent_status_log and fail (or double-emit in --sql/offline mode,
# where checkfirst has nothing to check against).
agent_status_enum = postgresql.ENUM(
    "pending_approval", "approved", "deactivated", "rejected",
    name="auth_agent_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute(
        "CREATE TYPE auth_agent_status AS ENUM "
        "('pending_approval', 'approved', 'deactivated', 'rejected')"
    )

    op.create_table(
        "auth_end_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", postgresql.CITEXT(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "auth_delivery_agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=False, unique=True),
        sa.Column("photo_url", sa.Text(), nullable=False),
        sa.Column("status", agent_status_enum, nullable=False, server_default="pending_approval"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "auth_admin_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text(f"'{ADMIN_SINGLETON_ID}'::uuid")),
        sa.Column("username", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("recovery_email", postgresql.CITEXT(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"id = '{ADMIN_SINGLETON_ID}'::uuid", name="auth_admin_accounts_singleton"),
    )
    # TRD-AUTH-001: the CHECK + fixed-default PK means a second row can only ever be
    # inserted with the same id, which the PRIMARY KEY constraint then rejects outright.

    op.create_table(
        "auth_otp_codes",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("code_hash", sa.Text(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('end_user', 'delivery_agent')", name="ck_auth_otp_codes_role"),
    )
    op.create_index(
        "ix_auth_otp_codes_email_role_issued",
        "auth_otp_codes",
        ["email", "role", sa.text("issued_at DESC")],
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("jti_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('end_user', 'delivery_agent', 'admin')", name="ck_auth_sessions_role"),
    )
    op.create_index("ix_auth_sessions_jti_hash", "auth_sessions", ["jti_hash"], unique=True)

    op.create_table(
        "auth_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("admin_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth_admin_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "auth_agent_status_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth_delivery_agents.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("old_status", agent_status_enum, nullable=False),
        sa.Column("new_status", agent_status_enum, nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth_admin_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_auth_agent_status_log_agent", "auth_agent_status_log", ["agent_id", "changed_at"])

    # Singleton Admin seed. Hashed with Argon2id (TRD-AUTH-002) at migration
    # run time from ADMIN_SEED_PASSWORD — the plaintext is never written to
    # this file, a log, or git; only the resulting hash reaches the database.
    password_hash = PasswordHasher().hash(ADMIN_SEED_PASSWORD)
    op.execute(
        sa.text(
            "INSERT INTO auth_admin_accounts (id, username, password_hash, recovery_email) "
            "VALUES (:id, :username, :password_hash, :recovery_email)"
        ).bindparams(
            # A plain str bind param compiles to ::VARCHAR against asyncpg,
            # which Postgres refuses to implicitly cast into a uuid column
            # (found by actually running this migration for the first time,
            # while wiring up TASK-AUTH-018's e2e infra) — a real uuid.UUID
            # value lets SQLAlchemy infer the correct bind type instead.
            id=uuid.UUID(ADMIN_SINGLETON_ID),
            username=ADMIN_SEED_USERNAME,
            password_hash=password_hash,
            recovery_email=ADMIN_SEED_EMAIL,
        )
    )


def downgrade() -> None:
    op.drop_table("auth_agent_status_log")
    op.drop_table("auth_reset_tokens")
    op.drop_index("ix_auth_sessions_jti_hash", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_index("ix_auth_otp_codes_email_role_issued", table_name="auth_otp_codes")
    op.drop_table("auth_otp_codes")
    op.drop_table("auth_admin_accounts")
    op.drop_table("auth_delivery_agents")
    op.drop_table("auth_end_users")
    op.execute("DROP TYPE auth_agent_status")
