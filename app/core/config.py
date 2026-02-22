from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Autopilot AI Tooling MVP"
    database_url: str = "sqlite:///./autopilot.db"
    object_store_path: str = "data/object_store"
    opensearch_url: str | None = None
    opensearch_index: str = "autopilot-assets"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")


settings = Settings()
