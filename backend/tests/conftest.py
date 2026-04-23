from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.config import reset_settings_cache
from backend.api.database import get_session_factory, reset_database_state


@pytest.fixture
def backend_env(tmp_path, monkeypatch) -> Generator[str, None, None]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    monkeypatch.delenv("OPENCLAW_BACKEND_DATABASE_PATH", raising=False)
    reset_settings_cache()
    reset_database_state()
    yield database_url
    reset_database_state()
    reset_settings_cache()
    os.environ.pop("OPENCLAW_BACKEND_DATABASE_URL", None)


@pytest.fixture
def app(backend_env):
    from backend.api.main import create_app

    return create_app()


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(app) -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
