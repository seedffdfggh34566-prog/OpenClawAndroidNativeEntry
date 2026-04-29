from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "AI Sales Assistant Backend"
    database_url: str | None = None
    database_path: str = "data/app.db"
    recent_items_limit: int = 5
    log_level: str = "INFO"
    log_json: bool = True
    langfuse_enabled: bool = False
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    llm_provider: str = "tencent_tokenhub"
    llm_base_url: str = "https://tokenhub.tencentmaas.com/v1"
    llm_model: str = "minimax-m2.5"
    llm_api_key: str | None = None
    llm_prompt_version: str = "product_learning_llm_v1"
    llm_timeout_seconds: float = 30.0
    sales_agent_runtime_mode: str = "deterministic"
    sales_agent_llm_prompt_version: str = "sales_agent_turn_llm_v1"
    dev_llm_trace_enabled: bool = False
    dev_llm_trace_dir: str = "/tmp/openclaw_llm_traces"
    dev_sales_workspace_diagnostics_enabled: bool = False
    sales_workspace_store_backend: str | None = None
    sales_workspace_store_dir: str | None = None

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
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite:///{self.database_file}"

    @property
    def uses_sqlite(self) -> bool:
        return self.resolved_database_url.startswith("sqlite")

    @property
    def sales_workspace_store_path(self) -> Path | None:
        if not self.sales_workspace_store_dir:
            return None
        path = Path(self.sales_workspace_store_dir)
        if path.is_absolute():
            return path
        return BACKEND_ROOT / path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
