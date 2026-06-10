import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("APP_ENV", "development")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env" if ENV != "test" else None,  # ← ne charge pas .env en test
        env_file_encoding="utf-8"
    )

    secret_key: SecretStr = SecretStr("test-secret")  # ← valeur par défaut
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    aws_access_key_id: str = "fake"
    aws_secret_access_key: str = "fake"
    aws_region: str = "eu-west-1"
    aws_bucket_name: str = "fake"

    connection_string: str = "sqlite:///:memory:"
    postgres_user: str = "fake"
    postgres_password: str = "fake"
    postgres_server: str = "fake"
    postgres_port: str = "5432"
    postgres_db: str = "fake"

    app_env: str = "development"  
    cookie_domain: str = "localhost"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

settings = Settings()


