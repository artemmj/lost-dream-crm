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
    redis_password: SecretStr = Field(default="", alias="REDIS_PASSWORD")

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf8",
        extra="ignore",
    )

    @property
    def redis_url(self):
        # redis://[:password@]host:port/db — пароль опционален (пустая строка = без auth)
        password_part = (
            f":{self.redis_password.get_secret_value()}@"
            if self.redis_password.get_secret_value()
            else ""
        )
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"


class Settings(BaseSettings):
    # URL service-auth для валидации токенов и проверки пермишенов
    auth_service_url: str = Field(
        default="http://service-auth:8000", alias="AUTH_SERVICE_URL"
    )

    db_settings: DBSettings = DBSettings()
    redis_settings: RedisSettings = RedisSettings()

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf8",
        extra="ignore",
    )


settings = Settings()
