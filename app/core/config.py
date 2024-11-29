from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    WHATSAPP_API_TOKEN: str = "development_token"
    WHATSAPP_PHONE_NUMBER_ID: str = "development_id"
    WHATSAPP_BUSINESS_ID: str = "development_business_id"
    WEBHOOK_VERIFY_TOKEN: str = "development_webhook_token"
    DATABASE_URL: str = "sqlite:///messages.db"
    INSTAGRAM_ACCESS_TOKEN: str = "development_instagram_token"
    INSTAGRAM_ACCOUNT_ID: str = "development_instagram_id"

    # Security
    SECRET_KEY: str = "development_secret_key"
    ALLOWED_HOSTS: List[str] = ["*"]
    ENVIRONMENT: str = "production"
    
    # Rate limiting
    RATE_LIMIT: str = "100/minute"
    
    # Redis cache
    REDIS_URL: str = "redis://localhost:6379"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Database
    DB_MAX_CONNECTIONS: int = 100
    DB_MIN_CONNECTIONS: int = 20
    DB_CONNECTION_TIMEOUT: int = 5000
    
    # API Timeouts
    API_TIMEOUT: int = 30
    
    # JWT Settings
    JWT_SECRET_KEY: str = "development_jwt_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def is_production(self):
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self):
        return self.ENVIRONMENT.lower() == "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
