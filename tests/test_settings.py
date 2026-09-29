from config.settings import settings
import pytest
from pydantic import ValidationError


def test_settings_load():
    assert settings.app_name
    assert settings.app_env == "development"
    assert settings.default_language == "es"
