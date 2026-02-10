"""
Global configuration settings for Finito App Backend application.
Environment variables are loaded from the .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""

    # Basic
    app_name: str = "Finito App Backend"
    app_version: str = "0.1.0"
    debug: bool = False

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "finito_app"

    # API
    api_v1_str: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a unique instance of configuration settings (singleton pattern).
    Uses cache to avoid unnecessary recreations.
    """
    return Settings()
