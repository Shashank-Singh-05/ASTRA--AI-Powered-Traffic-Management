"""ASTRA Backend Configuration - Settings loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import List
import os
import secrets

class Settings(BaseSettings):
    """Application settings loaded from .env file or environment variables."""

    # App
    APP_NAME: str = "ASTRA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/astra"

    # JWT Auth (Generated randomly on startup so sessions clear on restart)
    SECRET_KEY: str = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Gemini AI
    GEMINI_API_KEY: str = ""

    # Paths
    MODELS_DIR: str = "./models"
    DATA_DIR: str = "./data"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
