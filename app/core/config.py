from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "todo-service"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/todo"

    # API
    api_v1_prefix: str = ""


settings = Settings()
