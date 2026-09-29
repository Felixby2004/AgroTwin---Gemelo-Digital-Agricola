from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Participatory Agricultural Digital Twin"
    app_env: str = "development"
    debug: bool = True
    default_language: str = "es"

    data_dir: str = "data"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    model_dir: str = "data/models"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    jwt_secret_key: str = (
        "development-only-secret"
    )

    jwt_algorithm: str = "HS256"

    jwt_access_token_minutes: int = 60


settings = Settings()