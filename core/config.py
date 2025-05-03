from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os


class Settings(BaseSettings):
    """
    Configuration settings for our application.
    """
    openweather_api_key: str = "dummy_key"
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    admin_username: str = "admin"
    secret_key: str = "secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./data/weather.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

    @property
    def database_path(self) -> Path:
        """
        Function that returns path to database.
        :return: path to database
        """
        return Path(os.path.abspath(os.getcwd())) / "data"


settings = Settings()
