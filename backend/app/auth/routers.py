from fastapi import APIRouter

# Routes land here starting with TASK-AUTH-006 (OTP issuance). Prefix matches
# interface-01 BACKEND_API's /v1/auth/* route group (system-architecture.md).
router = APIRouter(prefix="/v1/auth", tags=["auth"])
