from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "AI Sales Assistant Backend"
    database_path: str = "data/app.db"
    runtime_allow_draft_profiles: bool = True
    recent_items_limit: int = 5

    model_config = SettingsConfigDict(
        env_prefix="OPENCLAW_BACKEND_",
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_file(self) -> Path:
        path = Path(self.database_path)
        if path.is_absolute():
            return path
        return BACKEND_ROOT / path

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_file}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
