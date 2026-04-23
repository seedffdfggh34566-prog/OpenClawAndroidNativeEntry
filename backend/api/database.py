from __future__ import annotations

from collections.abc import Generator
from typing import Any

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import Session, sessionmaker

from backend.api.config import BACKEND_ROOT, get_settings
from backend.api.models import Base

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_engine_url: str | None = None

_REPO_ROOT = BACKEND_ROOT.parent
_ALEMBIC_REQUIRED_TABLES = {
    "product_profiles",
    "lead_analysis_results",
    "analysis_reports",
    "agent_runs",
}


def get_engine() -> Engine:
    global _engine, _engine_url

    settings = get_settings()
    if _engine is None or _engine_url != settings.resolved_database_url:
        if settings.uses_sqlite:
            settings.database_file.parent.mkdir(parents=True, exist_ok=True)

        connect_args = {"check_same_thread": False} if settings.uses_sqlite else {}
        _engine = create_engine(
            settings.resolved_database_url,
            connect_args=connect_args,
            future=True,
        )
        _engine_url = settings.resolved_database_url
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory

    if _session_factory is None or _engine_url != get_settings().resolved_database_url:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            future=True,
        )
    return _session_factory


def get_db_session() -> Generator[Session, Any, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    engine = get_engine()
    if _should_stamp_existing_database(engine):
        stamp_database("head")
    upgrade_database("head")


def reset_database_state() -> None:
    global _engine, _session_factory, _engine_url

    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
    _engine_url = None


def get_alembic_config() -> Config:
    config = Config(str(_REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", get_settings().resolved_database_url)
    return config


def upgrade_database(revision: str = "head") -> None:
    command.upgrade(get_alembic_config(), revision)


def stamp_database(revision: str = "head") -> None:
    command.stamp(get_alembic_config(), revision)


def _should_stamp_existing_database(engine: Engine) -> bool:
    inspector = sqlalchemy_inspect(engine)
    table_names = set(inspector.get_table_names())
    if "alembic_version" in table_names:
        return False
    return bool(table_names & _ALEMBIC_REQUIRED_TABLES)
