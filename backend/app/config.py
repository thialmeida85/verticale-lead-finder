from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Verticale Lead Finder"
    cors_origins: str = "http://localhost:5173"
    cnpj_api_base_url: str = "https://publica.cnpj.ws/cnpj"
    cnpj_api_key: str | None = None
    exports_dir: str = "../exports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def export_path(self) -> Path:
        return Path(self.exports_dir).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
