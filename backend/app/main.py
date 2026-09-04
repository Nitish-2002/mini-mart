from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.auth.routers import router as auth_router
from app.auth.schemas import ErrorOut
from app.core.rate_limit import limiter

app = FastAPI(title="Mini Mart API", version="v1")

app.state.limiter = limiter


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # Every error body in this API is a bare ErrorOut shape ({"error": ...}),
    # never FastAPI's default {"detail": ...} envelope — get_current_user()/
    # require_role() (decision-76, shared by every future protected route in
    # every module) raise plain HTTPException, so this unwraps their
    # dict-shaped `detail` to match every other endpoint's hand-built
    # JSONResponse instead of leaving it double-wrapped.
    content = exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    # decision-73's window is a flat 15 minutes; 900s is the worst-case wait
    # from the moment a caller trips the limit, not always the exact reset
    # time (slowapi's fixed-window storage doesn't expose that precisely) —
    # an honest approximation, not a promise of the exact second.
    return JSONResponse(
        status_code=429,
        content=ErrorOut(error="rate_limited", retry_after_seconds=900).model_dump(
            exclude_none=True
        ),
    )


app.include_router(auth_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
