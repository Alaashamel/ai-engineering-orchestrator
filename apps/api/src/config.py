import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


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
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"
    webhook_url: str = ""
    web_origin: str = "http://localhost:5173"
    otlp_endpoint: str = ""


    def production_warnings(self) -> list[str]:
        """Returns human-readable warnings about settings that look unsafe
        for a production environment. Named to avoid colliding with
        pydantic's own BaseModel.validate classmethod."""
        warnings: list[str] = []
        if self.environment == "production":
            if self.jwt_secret == "dev-secret-change-in-production":
                warnings.append("JWT_SECRET is still the default development value")
            if not self.database_url or "localhost" in self.database_url:
                warnings.append("DATABASE_URL points to localhost in production mode")
        return warnings


settings = Settings()
