from app.config import Settings
from app.services.gemini_service import GeminiConfigurationError, GeminiService


def test_default_gemini_model():
    settings = Settings(gemini_api_key="configured")

    assert settings.gemini_model == "gemini-3.8-flash"


def test_gemini_model_can_be_overridden_by_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "supported-custom-model")

    settings = Settings(gemini_api_key="configured")

    assert settings.gemini_model == "supported-custom-model"


def test_health_and_gemini_service_use_the_same_configuration_predicate():
    for key, expected in (("", False), ("   ", False), ("configured", True)):
        settings = Settings(gemini_api_key=key)

        assert settings.gemini_configured is expected
        if expected:
            continue

        try:
            GeminiService(settings)
        except GeminiConfigurationError as exc:
            assert str(exc) == "GEMINI_API_KEY is not configured."
        else:
            raise AssertionError("GeminiService accepted an unconfigured key")
