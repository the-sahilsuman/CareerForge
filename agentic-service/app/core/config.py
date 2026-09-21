from functools import lru_cache
from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Values are loaded from environment variables / .env.
    Environment variable names are case-insensitive.
    """

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    email_token_encryption_key: str

    internal_service_key: str
    core_backend_url: str

    # =========================================================
    # Application
    # =========================================================

    app_name: str = "CareerForge Agentic Service"
    app_version: str = "1.0.0"

    debug: bool = False
    log_level: str = "INFO"

    # =========================================================
    # PostgreSQL
    # =========================================================

    database_url: str

    # =========================================================
    # AWS
    # =========================================================

    aws_region: str = "ap-south-1"
    aws_startup_check: bool = False

    # =========================================================
    # ElastiCache / Redis
    # =========================================================

    redis_host: str
    redis_port: int = 6379

    redis_username: str
    redis_password: str

    redis_ssl: bool = True

    # Temporary chat memory.
    # One chat session lives in Redis for one hour.
    chat_memory_ttl_seconds: int = 3600
    redis_session_ttl: int = 3600

    # Optional CA certificate for TLS verification.
    redis_ca_cert: str | None = None

    

    # =========================================================
    # S3
    # =========================================================

    resume_s3_bucket_name: str | None = None
    s3_bucket: str | None = None

    # =========================================================
    # S3 Vectors
    # =========================================================

    s3_vector_bucket_name: str | None = None
    s3_vector_index_name: str | None = None
    s3_vector_index_arn: str | None = None

    # =========================================================
    # Ingestion Queue
    # =========================================================

    ingestion_queue_url: str | None = None

    sqs_max_messages: int = 5
    sqs_wait_time_seconds: int = 20
    sqs_visibility_timeout: int = 300
    sqs_error_retry_seconds: int = 5

    chunk_size: int = 1000
    chunk_overlap: int = 150

    # =========================================================
    # LLM
    # =========================================================

    llm_provider: str = "gemini"

    llm_temperature: float = 0.2
    llm_max_tokens: int = 2048
    

    bedrock_model_id: str | None = None
    bedrock_aws_region: str = "us-east-1"

    gemini_model_id: str = "gemini-2.5-flash"
    google_api_key: str | None = None

    openai_api_key: str | None = None
    openai_model_id: str = "gpt-5-mini"

    huggingface_api_key: str | None = None
    huggingface_llm_model_id: str | None = None
    huggingface_base_url: str = (
        "https://router.huggingface.co/v1"
    )

    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    openrouter_llm_model: str = (
        "nvidia/nemotron-3-ultra-550b-a55b:free"
    )

    # =========================================================
    # Embeddings
    # =========================================================

    embedding_provider: str = "bedrock"

    embedding_dimensions: int = 1024

    bedrock_embedding_model_id: str = (
        "amazon.titan-embed-text-v2:0"
    )

    gemini_embedding_model: str = (
        "models/gemini-embedding-001"
    )

    huggingface_embedding_model: str | None = None

    openrouter_embedding_model: str = (
    "nvidia/nemotron-3-embed-1b:free"
    )

    openrouter_embedding_dimensions: int = 1024

    # =========================================================
    # Configuration
    # =========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # =========================================================
    # Redis URL
    # =========================================================

    @property
    def redis_url(self) -> str:
        """
        Build the Redis connection URL.

        Uses:
            redis://  for non-TLS
            rediss:// for TLS
        """

        scheme = "rediss" if self.redis_ssl else "redis"

        username = quote(
            self.redis_username,
            safe="",
        )

        password = quote(
            self.redis_password,
            safe="",
        )

        return (
            f"{scheme}://"
            f"{username}:{password}"
            f"@{self.redis_host}:{self.redis_port}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Return the singleton application settings object.
    """
    return Settings()


settings = get_settings()