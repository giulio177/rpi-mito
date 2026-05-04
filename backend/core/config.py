import sys
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "RPi Car Infotainment"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    # Default: 'mock' on Mac/Win, 'real' on Linux (Raspberry Pi)
    # Override with HAL_MODE=real in .env or environment
    hal_mode: str = "real" if sys.platform.startswith("linux") else "mock"

    audio_mixer_control: str = "Master"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()