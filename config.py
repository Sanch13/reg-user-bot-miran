from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_TELEGRAM_TOKEN: SecretStr
    CHANNEL_LINK: str
    CHANNEL_ID_MIRAN: str

    DATABASE: str

    SMTP_SERVER: str
    PORT: int
    SENDER_EMAIL: str
    PASSWORD: str
    SUBJECT: str
    BODY: str
    TO_EMAIL: str
    TO_EMAILS: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
