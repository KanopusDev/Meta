from pydantic import BaseSettings

class Settings(BaseSettings):
    WHATSAPP_API_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    VERIFY_TOKEN: str
    WHATSAPP_BUSINESS_ID: str
    INSTAGRAM_ACCESS_TOKEN: str
    INSTAGRAM_ACCOUNT_ID: str
    
    class Config:
        env_file = ".env"

settings = Settings()
