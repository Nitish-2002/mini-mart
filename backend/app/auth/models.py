"""SQLAlchemy models for AUTH's 7 tables. Schema is fixed in
trd.md's Data Model / DDL and §5a Persistence Constraints — this file is a
literal transcription, not a redesign. Do not add columns, indexes, or
constraints here without a corresponding TRD change (`/daksh change AUTH`).
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# TRD-AUTH-001 (inv-auth-singleton-admin): fixed literal, never generated.
ADMIN_SINGLETON_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# One native Postgres ENUM TYPE, reused across auth_delivery_agents.status and
# auth_agent_status_log.old_status/new_status — matches the DDL's single
# `CREATE TYPE auth_agent_status AS ENUM (...)` exactly (trd.md's Data Model).
agent_status_enum = Enum(
    "pending_approval", "approved", "deactivated", "rejected",
    name="auth_agent_status",
)

OTP_ROLE_VALUES = ("end_user", "delivery_agent")
SESSION_ROLE_VALUES = ("end_user", "delivery_agent", "admin")


class AuthEndUser(Base):
    __tablename__ = "auth_end_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class AuthDeliveryAgent(Base):
    __tablename__ = "auth_delivery_agents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)
    photo_url: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(agent_status_enum, nullable=False, server_default="pending_approval")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class AuthAdminAccount(Base):
    __tablename__ = "auth_admin_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=ADMIN_SINGLETON_ID)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    recovery_email: Mapped[str] = mapped_column(CITEXT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # TRD-AUTH-001: the CHECK + fixed-default PK means a second row can only ever be
    # inserted with the same id, which the PRIMARY KEY constraint then rejects outright.
    __table_args__ = (
        CheckConstraint(
            f"id = '{ADMIN_SINGLETON_ID}'::uuid",
            name="auth_admin_accounts_singleton",
        ),
    )


class AuthOtpCode(Base):
    __tablename__ = "auth_otp_codes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(CITEXT, nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    code_hash: Mapped[str] = mapped_column(nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(f"role IN {OTP_ROLE_VALUES}", name="ck_auth_otp_codes_role"),
        Index("ix_auth_otp_codes_email_role_issued", "email", "role", issued_at.desc()),
    )


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    jti_hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    role: Mapped[str] = mapped_column(nullable=False)
    # app-enforced reference into auth_end_users/auth_delivery_agents/auth_admin_accounts
    # by role — no DB foreign key, per trd.md §5a's documented polymorphic-reference gap.
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(f"role IN {SESSION_ROLE_VALUES}", name="ck_auth_sessions_role"),
    )


class AuthResetToken(Base):
    __tablename__ = "auth_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    admin_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth_admin_accounts.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuthAgentStatusLog(Base):
    __tablename__ = "auth_agent_status_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth_delivery_agents.id", ondelete="RESTRICT"), nullable=False
    )
    old_status: Mapped[str] = mapped_column(agent_status_enum, nullable=False)
    new_status: Mapped[str] = mapped_column(agent_status_enum, nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth_admin_accounts.id", ondelete="RESTRICT"), nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_auth_agent_status_log_agent", "agent_id", "changed_at"),
    )
