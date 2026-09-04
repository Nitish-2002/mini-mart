import uuid

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services
from app.auth.dependencies import Principal, get_current_user, require_role
from app.auth.schemas import (
    AdminLoginIn,
    AdminLoginOut,
    AdminPasswordResetConfirmIn,
    AdminPasswordResetRequestIn,
    AgentRegisterIn,
    AgentRegisterOut,
    AgentStatusUpdateIn,
    AgentStatusUpdateOut,
    ErrorOut,
    OtpRequestIn,
    OtpRequestOut,
    OtpVerifyIn,
    OtpVerifyOut,
)
from app.auth.session import IssuedSession, clear_session_cookie, revoke_session, set_session_cookie
from app.core.db import get_session
from app.core.rate_limit import limiter

# Prefix matches interface-01 BACKEND_API's /v1/auth/* route group
# (system-architecture.md).
router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post(
    "/otp/request",
    response_model=OtpRequestOut,
    status_code=202,
    responses={429: {"model": ErrorOut}},
)
async def otp_request(
    body: OtpRequestIn, session: AsyncSession = Depends(get_session)
) -> OtpRequestOut | JSONResponse:
    try:
        result = await services.request_otp(session, body.email, body.role)
    except services.RateLimitExceeded as exc:
        return JSONResponse(
            status_code=429,
            content=ErrorOut(
                error="rate_limited", retry_after_seconds=exc.retry_after_seconds
            ).model_dump(exclude_none=True),
        )
    return OtpRequestOut(
        cooldown_seconds=result.cooldown_seconds,
        expires_in_seconds=result.expires_in_seconds,
    )


@router.post(
    "/otp/verify",
    response_model=OtpVerifyOut,
    responses={401: {"model": ErrorOut}, 410: {"model": ErrorOut}},
)
async def otp_verify(
    body: OtpVerifyIn, response: Response, session: AsyncSession = Depends(get_session)
) -> OtpVerifyOut | JSONResponse:
    try:
        result = await services.verify_otp(session, body.email, body.code, body.role)
    except services.InvalidCode:
        return JSONResponse(
            status_code=401, content=ErrorOut(error="invalid_code").model_dump(exclude_none=True)
        )
    except services.CodeExpired:
        return JSONResponse(
            status_code=410, content=ErrorOut(error="code_expired").model_dump(exclude_none=True)
        )
    # CR-004: session delivered via Set-Cookie only, never in this body.
    set_session_cookie(
        response, IssuedSession(token=result.session_token, expires_at=result.expires_at)
    )
    return OtpVerifyOut(role=result.role, expires_at=result.expires_at.isoformat())


@router.post(
    "/agent/register",
    response_model=AgentRegisterOut,
    status_code=201,
    responses={409: {"model": ErrorOut}},
)
async def agent_register(
    body: AgentRegisterIn, session: AsyncSession = Depends(get_session)
) -> AgentRegisterOut | JSONResponse:
    try:
        await services.register_agent(session, body.name, body.phone, body.email, body.photo_url)
    except services.EmailAlreadyRegistered:
        return JSONResponse(
            status_code=409,
            content=ErrorOut(error="email_already_registered").model_dump(exclude_none=True),
        )
    return AgentRegisterOut(status="pending_approval")


@router.post(
    "/agent/{agent_id}/status",
    response_model=AgentStatusUpdateOut,
    responses={404: {"model": ErrorOut}, 409: {"model": ErrorOut}},
)
async def agent_status_update(
    agent_id: uuid.UUID,
    body: AgentStatusUpdateIn,
    principal: Principal = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
) -> AgentStatusUpdateOut | JSONResponse:
    try:
        new_status = await services.update_agent_status(
            session, agent_id, body.action, principal.user_id
        )
    except services.AgentNotFound:
        return JSONResponse(
            status_code=404, content=ErrorOut(error="agent_not_found").model_dump(exclude_none=True)
        )
    except services.InvalidTransition:
        return JSONResponse(
            status_code=409,
            content=ErrorOut(error="invalid_transition").model_dump(exclude_none=True),
        )
    return AgentStatusUpdateOut(status=new_status)


@router.get("/agent/status", response_model=AgentStatusUpdateOut)
async def agent_status(
    principal: Principal = Depends(require_role("delivery_agent")),
    session: AsyncSession = Depends(get_session),
) -> AgentStatusUpdateOut:
    # Deliberately require_role, not require_approved_agent: a pending or
    # rejected agent must still be able to read their own status
    # (ss-auth-agent-status's whole purpose is answering that question).
    status = await services.get_agent_status(session, principal.user_id)
    return AgentStatusUpdateOut(status=status)


@router.post(
    "/admin/login",
    response_model=AdminLoginOut,
    responses={401: {"model": ErrorOut}, 429: {"model": ErrorOut}},
)
@limiter.limit("10/15minutes")  # decision-73: per-IP, defense-in-depth, not account lockout
async def admin_login(
    request: Request,
    body: AdminLoginIn,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> AdminLoginOut | JSONResponse:
    try:
        result = await services.admin_login(session, body.username, body.password)
    except services.InvalidCredentials:
        return JSONResponse(
            status_code=401,
            content=ErrorOut(error="invalid_credentials").model_dump(exclude_none=True),
        )
    set_session_cookie(
        response, IssuedSession(token=result.session_token, expires_at=result.expires_at)
    )
    return AdminLoginOut(expires_at=result.expires_at.isoformat())


@router.post("/admin/password-reset/request", status_code=202, response_model=None)
async def admin_password_reset_request(
    body: AdminPasswordResetRequestIn, session: AsyncSession = Depends(get_session)
) -> dict:
    # decision-77: identical 202 {} whether or not the email matched — no
    # try/except needed, the service itself never raises for a non-match.
    await services.request_password_reset(session, body.email)
    return {}


@router.post(
    "/admin/password-reset/confirm",
    response_model=None,
    responses={410: {"model": ErrorOut}},
)
async def admin_password_reset_confirm(
    body: AdminPasswordResetConfirmIn, response: Response, session: AsyncSession = Depends(get_session)
) -> dict | JSONResponse:
    try:
        result = await services.confirm_password_reset(session, body.token, body.new_password)
    except services.ResetTokenInvalid:
        return JSONResponse(
            status_code=410,
            content=ErrorOut(error="token_expired_or_used").model_dump(exclude_none=True),
        )
    set_session_cookie(
        response, IssuedSession(token=result.session_token, expires_at=result.expires_at)
    )
    return {}


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    principal: Principal = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await revoke_session(session, principal.jti)
    clear_session_cookie(response)
