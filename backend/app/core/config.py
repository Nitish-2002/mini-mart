from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project-wide settings shared by every module. Module-specific secrets
    (e.g. AUTH's JWT signing key) live in that module's own config, per the
    import-discipline module boundary (decision-33, system-architecture.md).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Defaults match docker-compose's LOCAL Postgres service (env-01, system-architecture.md).
    # PREVIEW/PRODUCTION always inject a real DATABASE_URL — this default is never reachable there.
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/minimart"

    # FRONTEND is one deployable (CR-007) at its own origin, separate from
    # this backend — cross-origin credentialed fetches (CR-004's httpOnly
    # cookie) need CORS explicitly allowing it, or the browser blocks every
    # request before it reaches the app at all. Comma-separated; PREVIEW/
    # PRODUCTION inject their own real origin once oq-27 resolves.
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


settings = Settings()
