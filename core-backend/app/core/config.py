from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CareerForge Core Backend"
    debug: bool = False

    agentic_service_url: str
    agentic_internal_service_key: str

    database_url: str

    frontend_url: str

    aws_region: str
    ingestion_queue_url: str | None = None
    ingestion_dlq_url: str | None = None
    s3_bucket_name: str
    aws_bucket_name: str

    cognito_user_pool_id: str
    cognito_client_id: str

    cors_origins: str = "http://localhost:5173"

    email_token_encryption_key: str

    log_level: str = "INFO"

    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_oauth_state_secret: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cognito_issuer(self) -> str:
        return (
            f"https://cognito-idp.{self.aws_region}.amazonaws.com/"
            f"{self.cognito_user_pool_id}"
        )

    @property
    def cognito_jwks_url(self) -> str:
        return f"{self.cognito_issuer}/.well-known/jwks.json"


settings = Settings()