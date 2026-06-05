from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("APP_ENV") != "test" else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    RAPIDAPI_PROXY_SECRET: str = ""
    # Set this if the API is served under a sub-path behind a proxy.
    # Leave empty for normal Coolify deployments (served at domain root).
    ROOT_PATH: str = ""
    # OpenRouter fallback — used automatically only if the Groq call fails.
    # Leave OPENROUTER_API_KEY empty to disable the fallback entirely.
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct"

    @property
    def openrouter_enabled(self) -> bool:
        return bool(self.OPENROUTER_API_KEY)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def is_dev_or_test(self) -> bool:
        return self.APP_ENV.lower() in ("development", "test")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
