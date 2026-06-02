from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """各種設定を管理する"""
    secret: str | None = None
    algorithm: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
