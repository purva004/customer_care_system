from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    database_url: str = Field(default="sqlite+aiosqlite:///./data/app.db", alias="DATABASE_URL")

    # Twilio
    twilio_auth_token: str | None = Field(default=None, alias="TWILIO_AUTH_TOKEN")

    # AI providers (optional)
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    # CRM integration
    crm_api_base_url: str | None = Field(default=None, alias="CRM_API_BASE_URL")
    crm_api_token: str | None = Field(default=None, alias="CRM_API_TOKEN")
    crm_timeout_seconds: float = Field(default=3.0, alias="CRM_TIMEOUT_SECONDS")

    # Defaults for personalization
    default_language: str = Field(default="en-US", alias="DEFAULT_LANGUAGE")
    default_gender: str = Field(default="neutral", alias="DEFAULT_GENDER")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

