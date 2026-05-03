from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "RPi Car Infotainment"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    hal_mode: str = "mock"

    audio_mixer_control: str = "Master"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
    