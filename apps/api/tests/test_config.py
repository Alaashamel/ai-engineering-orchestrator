from src.config import settings


def test_settings_have_defaults():
    assert settings.database_url is not None
    assert settings.log_level is not None
    assert settings.environment == "development"
