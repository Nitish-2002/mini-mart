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


settings = Settings()
