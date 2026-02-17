from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Weeks Until Diploma"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/diplom_monitor"
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_FOR_DEV_ONLY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100  #  days
    TELEGRAM_BOT_TOKEN: str = "SET_YOUR_BOT_TOKEN"
    TELEGRAM_BOT_NAME: str = "weeks_until_diploma_bot"

    class Config:
        env_file = ".env"

settings = Settings()
