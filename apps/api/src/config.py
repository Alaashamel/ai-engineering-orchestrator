from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+asyncpg://app:app_password@localhost:5432/ai_software_company"
    )
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-secret-change-in-production"
    log_level: str = "DEBUG"
    environment: str = "development"


settings = Settings()
