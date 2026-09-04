from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services
from app.auth.schemas import (
    AgentRegisterIn,
    AgentRegisterOut,
    ErrorOut,
    OtpRequestIn,
    OtpRequestOut,
    OtpVerifyIn,
    OtpVerifyOut,
)
from app.core.db import get_session

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
    body: OtpVerifyIn, session: AsyncSession = Depends(get_session)
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
    return OtpVerifyOut(
        session_token=result.session_token,
        role=result.role,
        expires_at=result.expires_at.isoformat(),
    )


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
