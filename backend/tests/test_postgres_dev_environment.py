from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from sqlalchemy import inspect
from sqlalchemy import text

from backend.api.config import reset_settings_cache
from backend.api.database import get_engine
from backend.api.database import get_session_factory
from backend.api.database import init_db
from backend.api.database import reset_database_state

POSTGRES_VERIFY_ENV = "OPENCLAW_BACKEND_POSTGRES_VERIFY_URL"


@pytest.fixture
def postgres_dev_env(monkeypatch) -> Generator[str, None, None]:
    database_url = os.environ.get(POSTGRES_VERIFY_ENV)
    if not database_url:
        pytest.skip(f"set {POSTGRES_VERIFY_ENV} to run Postgres dev environment verification")

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    reset_settings_cache()
    reset_database_state()
    yield database_url
    reset_database_state()
    reset_settings_cache()


def test_postgres_dev_environment_runs_alembic_baseline(postgres_dev_env) -> None:
    init_db()

    engine = get_engine()
    assert engine.dialect.name == "postgresql"

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    assert "alembic_version" in table_names
    assert "product_profiles" in table_names
    assert "agent_runs" in table_names


def test_postgres_dev_environment_session_factory(postgres_dev_env) -> None:
    init_db()

    session = get_session_factory()()
    try:
        result = session.execute(text("SELECT 1")).scalar_one()
    finally:
        session.close()

    assert result == 1
