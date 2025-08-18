from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./rswarm.db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Deduplication
    DEDUPE_TTL_MINUTES: int = 10

    # WhatsApp
    WA_VERIFY_TOKEN: str = "your_verify_token"
    APP_SECRET: str = "your_app_secret"
    WA_BASE_URL: str = "https://graph.facebook.com/v15.0"
    WA_TOKEN: str = "your_wa_token"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
