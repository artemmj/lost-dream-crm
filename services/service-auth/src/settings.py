from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingModelConfigDefault:
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf8",
        extra="ignore",
    )


class DBSettings(BaseSettings, SettingModelConfigDefault):
    db_name: str = Field(default="db", alias="POSTGRES_NAME")
    db_user: str = Field(default="postgres", alias="POSTGRES_USER")
    db_password: SecretStr = Field(default="postgres", alias="POSTGRES_PASSWORD")
    db_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    db_port: int = Field(default=5433, alias="POSTGRES_PORT")
    db_echo: bool = Field(default=True, alias="POSTGRES_ECHO")

    @property
    def db_url(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password.get_secret_value()}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class Settings(BaseSettings, SettingModelConfigDefault):
    secret_key: SecretStr = Field(default="", alias="SECRET_KEY")

    db_settings: DBSettings = DBSettings()


settings = Settings()
