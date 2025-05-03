# app/config.py

from pydantic import EmailStr
from pydantic_settings import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    # JWT конфигурация
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # SMTP конфигурация
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str

    # Yoomoney настройки
    CONFIGURATION_ACCOUNT_ID: int
    CONFIGURATION_SECRET_KEY: str
    BASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

settings = Settings()
