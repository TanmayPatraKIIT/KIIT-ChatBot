"""
Configuration management using Pydantic settings.
Loads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application setting loaded from environment variables"""

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "kiit_chatbot"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_DB: int = 0
    REDIS_CELERY_DB: int = 1

    # LLM Configuration
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3:8b"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.7

    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_DEVICE: str = "cpu"

    # FAISS
    FAISS_INDEX_PATH: str = "/data/faiss_index.bin"
    FAISS_MAPPING_PATH: str = "/data/faiss_to_mongo_mapping.json"

    # Scraping
    SCRAPE_INTERVAL_HOURS: int = 6
    SCRAPE_TIMEOUT_SECONDS: int = 30
    SCRAPE_MAX_RETRIES: int = 3

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_RELOAD: bool = False

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/logs/app.log"

    # Security
    API_KEY: str = "your_secret_api_key_for_admin_endpoints"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
