"""
Configuration management using Pydantic settings.
Configured for Replit environment with PostgreSQL and OpenAI.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings for Replit environment"""

    # Database - PostgreSQL (Replit built-in)
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

    # OpenAI - Using Replit AI Integrations
    OPENAI_API_KEY: str = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.7


    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1
    API_RELOAD: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/tmp/app.log"

    # Security
    API_KEY: str = os.environ.get("API_KEY", "demo_api_key_change_in_production")
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")

    # Rate Limiting (in-memory)
    RATE_LIMIT_PER_MINUTE: int = 100

    # Cache TTL (in seconds)
    CACHE_TTL: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
