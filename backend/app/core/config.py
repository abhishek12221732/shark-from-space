"""
Application configuration settings.

Loads configuration from environment variables and .env file.
"""

import logging
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# Get the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB connection
    mongo_connection_string: str
    
    # API settings
    api_title: str = "Shark Foraging Project API"
    api_version: str = "1.0.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost",
        "http://localhost:5173",
    ]
    
    class Config:
        env_file = ENV_FILE_PATH
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()

logger.info(f"Configuration loaded from: {ENV_FILE_PATH}")

