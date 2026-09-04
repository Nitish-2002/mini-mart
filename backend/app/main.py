from fastapi import FastAPI

from app.auth.routers import router as auth_router

app = FastAPI(title="Mini Mart API", version="v1")

app.include_router(auth_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
