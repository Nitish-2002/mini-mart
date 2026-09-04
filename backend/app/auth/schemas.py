"""Pydantic request/response models for interface-auth-identity,
interface-auth-agent-mgmt, and interface-auth-admin-login. Field names and
shapes are a direct carry-forward from trd.md's API Contracts (including the
CR-002 `role` field) — never redesigned here.
"""

from typing import Literal

from pydantic import BaseModel, EmailStr

Role = Literal["end_user", "delivery_agent"]


class OtpRequestIn(BaseModel):
    email: EmailStr
    role: Role


class OtpRequestOut(BaseModel):
    cooldown_seconds: int
    expires_in_seconds: int


class OtpVerifyIn(BaseModel):
    email: EmailStr
    code: str
    role: Role


class OtpVerifyOut(BaseModel):
    # CR-004: no session_token field — delivered exclusively via Set-Cookie.
    role: Role
    expires_at: str


class AgentRegisterIn(BaseModel):
    name: str
    phone: str
    email: EmailStr
    photo_url: str


class AgentRegisterOut(BaseModel):
    status: Literal["pending_approval"]


AgentStatus = Literal["pending_approval", "approved", "deactivated", "rejected"]
AgentAction = Literal["approve", "reject", "deactivate", "reactivate"]


class AgentStatusUpdateIn(BaseModel):
    action: AgentAction


class AgentStatusUpdateOut(BaseModel):
    status: AgentStatus


class ErrorOut(BaseModel):
    error: str
    retry_after_seconds: int | None = None
