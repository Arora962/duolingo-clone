"""Shared pytest fixtures for the backend API."""

import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.config as config
import app.database as database
import app.main as main_module
import app.seed as seed_module
from app.database import Base


@pytest.fixture
def client(monkeypatch):
    """Create a fresh, FK-enforced SQLite application for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    test_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    monkeypatch.setenv("ENABLE_DEV_ENDPOINTS", "true")
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", test_session_local)
    monkeypatch.setattr(seed_module, "engine", engine)
    monkeypatch.setattr(seed_module, "SessionLocal", test_session_local)
    monkeypatch.setattr(main_module, "engine", engine)
    monkeypatch.setattr(config, "ENABLE_DEV_ENDPOINTS", True)

    Base.metadata.create_all(bind=engine)
    seed_module.seed()

    def override_get_db():
        db = test_session_local()
        try:
            yield db
        finally:
            db.close()

    main_module.app.dependency_overrides[database.get_db] = override_get_db

    with TestClient(main_module.app) as test_client:
        yield test_client

    main_module.app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def dev_disabled_client(monkeypatch):
    """Create an application with development routes disabled."""
    monkeypatch.setenv("ENABLE_DEV_ENDPOINTS", "false")
    reloaded_config = importlib.reload(config)
    reloaded_main = importlib.reload(main_module)
    assert reloaded_config.ENABLE_DEV_ENDPOINTS is False
    yield TestClient(reloaded_main.app)
    monkeypatch.setenv("ENABLE_DEV_ENDPOINTS", "true")
    importlib.reload(config)
    importlib.reload(main_module)
