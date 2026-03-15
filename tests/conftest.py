import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import SessionLocal
from main import app


@pytest.fixture(scope="session")
def api_key() -> str:
    return os.environ.get("API_KEY", "luna-static-api-key")


@pytest.fixture()
def client(api_key: str) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def auth_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key}


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
