from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from fte_api.main import app, db_engine


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_ok_when_database_reachable(client: TestClient) -> None:
    # SQLite in memory stands in for Postgres; /health only runs SELECT 1.
    app.dependency_overrides[db_engine] = lambda: create_engine("sqlite://")
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "database": "ok"}


def test_health_503_when_database_unreachable(client: TestClient) -> None:
    app.dependency_overrides[db_engine] = lambda: create_engine(
        "postgresql+psycopg://nobody:nopass@127.0.0.1:1/none?connect_timeout=1"
    )
    resp = client.get("/health")
    assert resp.status_code == 503
    assert resp.json() == {"status": "error", "database": "unreachable"}
