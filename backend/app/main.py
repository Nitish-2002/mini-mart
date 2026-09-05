import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.auth.routers import router as auth_router
from app.auth.schemas import ErrorOut
from app.core.config import settings
from app.core.rate_limit import limiter

app = FastAPI(title="Mini Mart API", version="v1")

app.state.limiter = limiter

# FRONTEND is a separate origin from this backend (CR-007) — the session
# cookie (CR-004, httpOnly) needs allow_credentials plus an explicit
# origin allowlist; "*" is rejected by browsers whenever credentials are
# involved, so there's no wildcard fallback here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

if os.environ.get("E2E_TEST_MODE"):
    # Only ever registered under Playwright's own webServer invocation
    # (frontend/playwright.config.ts sets this) — never in LOCAL/PREVIEW/
    # PRODUCTION, where the env var is simply unset.
    from app.e2e_testutils import router as e2e_test_router

    app.include_router(e2e_test_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
