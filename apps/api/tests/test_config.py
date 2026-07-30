from src.config import Settings, settings


def test_settings_have_defaults():
    assert settings.database_url is not None
    assert settings.log_level is not None
    assert settings.environment == "development"


def test_production_warnings_empty_in_development():
    assert settings.production_warnings() == []


def test_production_warnings_flags_default_jwt_secret():
    prod_settings = Settings(environment="production", database_url="postgresql+asyncpg://app:pw@db.example.com/prod")
    warnings = prod_settings.production_warnings()
    assert any("JWT_SECRET" in w for w in warnings)


def test_production_warnings_flags_localhost_database():
    prod_settings = Settings(environment="production", jwt_secret="a-real-secret")
    warnings = prod_settings.production_warnings()
    assert any("DATABASE_URL" in w for w in warnings)
