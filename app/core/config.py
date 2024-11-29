from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    WHATSAPP_API_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_BUSINESS_ID: str
    WEBHOOK_VERIFY_TOKEN: str
    DATABASE_URL: str
    INSTAGRAM_ACCESS_TOKEN: str
    INSTAGRAM_ACCOUNT_ID: str

    # Security
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["*"]
    ENVIRONMENT: str = "production"
    
    # Rate limiting
    RATE_LIMIT: str = "100/minute"
    
    # Redis cache
    REDIS_URL: str
    
    # Monitoring
    SENTRY_DSN: str = None
    
    # Database
    DB_MAX_CONNECTIONS: int = 100
    DB_MIN_CONNECTIONS: int = 20
    DB_CONNECTION_TIMEOUT: int = 5000
    
    # API Timeouts
    API_TIMEOUT: int = 30
    
    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def is_production(self):
        return self.ENVIRONMENT == "production"

    class Config:
        env_file = ".env"

settings = Settings()
