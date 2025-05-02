from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os


class Settings(BaseSettings):
    openweather_api_key: str
    admin_email: str
    admin_password: str
    admin_username: str
    secret_key: str = "secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./data/weather.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

    @property
    def database_path(self) -> Path:
        return Path(os.path.abspath(os.getcwd())) / "data"


settings = Settings()