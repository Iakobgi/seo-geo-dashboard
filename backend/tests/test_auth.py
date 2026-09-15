import os
import tempfile
from pathlib import Path

_database_file = Path(tempfile.mkstemp(suffix=".db")[1])
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_database_file.as_posix()}"
os.environ["SECRET_KEY"] = "test-auth-secret"
os.environ["FRONTEND_URL"] = "http://testserver"
os.environ["DEMO_USER_EMAIL"] = ""
os.environ["DEMO_AUDIT_URL"] = ""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    from app.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_register_login_and_me(client):
    email = "user@example.com"
    password = "TestPass123!"

    register_response = client.post(
        "/auth/register", json={"email": email, "password": password}
    )

    assert register_response.status_code == 200
    assert register_response.json()["email"] == email

    login_response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    me_response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email


def test_login_rejects_invalid_password(client):
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "TestPass123!"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_registration_rejects_duplicate_email(client):
    payload = {"email": "user@example.com", "password": "TestPass123!"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
