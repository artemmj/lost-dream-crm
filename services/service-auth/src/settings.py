from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    db_name: str = Field(default="db-crm", alias="POSTGRES_DB_NAME")
    db_user: str = Field(default="postgres", alias="POSTGRES_USER")
    db_password: SecretStr = Field(default="postgres", alias="POSTGRES_PASSWORD")
    db_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    db_port: int = Field(default=5432, alias="POSTGRES_PORT")
    db_echo: bool = Field(default=True, alias="POSTGRES_ECHO")

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf8",
        extra="ignore",
    )

    @property
    def db_url(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password.get_secret_value()}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class RedisSettings(BaseSettings):
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf8",
        extra="ignore",
    )

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


class Settings(BaseSettings):
    secret_key: SecretStr = Field(default="", alias="SECRET_KEY")
    access_token_expire: int = Field(default=120, alias="ACCESS_TOKEN_EXPIRE")

    db_settings: DBSettings = DBSettings()
    redis_settings: RedisSettings = RedisSettings()

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf8",
        extra="ignore",
    )


settings = Settings()
