from __future__ import annotations

from sqlalchemy import text
from sqlalchemy import inspect

from backend.api.database import get_engine, get_session_factory, init_db, reset_database_state
from backend.api.models import Base


def test_init_db_uses_alembic_and_creates_version_table(backend_env) -> None:
    init_db()

    inspector = inspect(get_engine())
    table_names = set(inspector.get_table_names())

    assert "alembic_version" in table_names
    assert "product_profiles" in table_names
    assert "agent_runs" in table_names


def test_init_db_stamps_existing_legacy_schema(backend_env) -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    reset_database_state()

    init_db()

    inspector = inspect(get_engine())
    assert "alembic_version" in inspector.get_table_names()


def test_session_factory_uses_configured_database_url(backend_env) -> None:
    init_db()

    session = get_session_factory()()
    try:
        result = session.execute(text("SELECT 1")).scalar_one()
    finally:
        session.close()

    assert result == 1
