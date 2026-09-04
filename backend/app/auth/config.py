from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """AUTH's own secrets — deliberately not on the shared app.core.Settings,
    since AUTH is the only module allowed to read/write credential/OTP data
    (system-architecture.md's Backend Architecture) and the only module
    these three should ever be wired into.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Local-dev-only placeholders — obviously fake so they can never pass for a
    # real secret. PREVIEW/PRODUCTION always inject real values (trd.md §10a).
    jwt_signing_secret: str = "local-dev-insecure-default-changeme"
    otp_hmac_pepper: str = "local-dev-insecure-default-changeme"
    resend_api_key: str = "local-dev-insecure-default-changeme"


auth_settings = AuthSettings()
