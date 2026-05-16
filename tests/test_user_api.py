import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from src.models.user_model import User
from src.service.auth_py import hash_password, get_current_user
from src.config.database import get_db
from main import app
from .conftest import TestingSessionLocal, override_get_db


# ───────────────────────────────────────────────
# Fixtures locales
# ───────────────────────────────────────────────

def make_mock_user(id: int = 1, email: str = "user@example.com") -> User:
    user = User()
    user.id = id
    user.email = email
    user.password_hashed = hash_password("password123")
    return user


@pytest.fixture
def seeded_db():
    """DB peuplée avec deux users : un normal, un admin."""
    session = TestingSessionLocal()

    user = User()
    user.email = "user@example.com"
    user.password_hashed = hash_password("password123")

    admin = User()
    admin.email = "admin1@gmail.com"
    admin.password_hashed = hash_password("adminpass")

    session.add_all([user, admin])
    session.commit()
    session.close()


@pytest.fixture
def client(seeded_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    def mock_user():
        return make_mock_user(id=1, email="user@example.com")
    app.dependency_overrides[get_current_user] = mock_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def admin_client(client):
    def mock_admin():
        return make_mock_user(id=2, email="admin1@gmail.com")
    app.dependency_overrides[get_current_user] = mock_admin
    yield client
    app.dependency_overrides.pop(get_current_user, None)


# ───────────────────────────────────────────────
# GET /api/users
# ───────────────────────────────────────────────

def test_get_all_users(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2  # user + admin seedés


# ───────────────────────────────────────────────
# GET /api/users/me
# ───────────────────────────────────────────────

def test_get_me_unauthenticated(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401

def test_get_me_authenticated(auth_client):
    response = auth_client.get("/api/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


# ───────────────────────────────────────────────
# GET /api/users/{user_id}
# ───────────────────────────────────────────────

def test_get_user_success(client):
    response = client.get("/api/users/1")
    assert response.status_code == 200

def test_get_user_not_found(client):
    response = client.get("/api/users/999")
    assert response.status_code == 404

def test_get_user_invalid_id(client):
    response = client.get("/api/users/abc")
    assert response.status_code == 422


# ───────────────────────────────────────────────
# POST /api/users
# ───────────────────────────────────────────────

def test_create_user_success(client):
    response = client.post(
        "/api/users",
        json={"email": "new@example.com", "password": "newpass123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"

def test_create_user_duplicate_email(client):
    # Email déjà seedé
    response = client.post(
        "/api/users",
        json={"email": "user@example.com", "password": "whatever"},
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_create_user_email_case_insensitive(client):
    # Même email en majuscules → doit être refusé
    response = client.post(
        "/api/users",
        json={"email": "USER@EXAMPLE.COM", "password": "whatever"},
    )
    assert response.status_code == 400

def test_create_user_invalid_payload(client):
    response = client.post("/api/users", json={"email": "missing-password@x.com"})
    assert response.status_code == 422


# ───────────────────────────────────────────────
# POST /api/users/token (login)
# ───────────────────────────────────────────────

def test_login_success(client):
    response = client.post(
        "/api/users/token",
        data={"username": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "message" in response.json()


def test_login_wrong_password(client):
    response = client.post(
        "/api/users/token",
        data={"username": "user@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401

def test_login_unknown_email(client):
    response = client.post(
        "/api/users/token",
        data={"username": "ghost@example.com", "password": "whatever"},
    )
    assert response.status_code == 401

def test_login_case_insensitive_email(client):
    response = client.post(
        "/api/users/token",
        data={"username": "USER@EXAMPLE.COM", "password": "password123"},
    )
    assert response.status_code == 200


# ───────────────────────────────────────────────
# PUT /api/users/{user_id}
# ───────────────────────────────────────────────

def test_update_user_success(client):
    response = client.put(
        "/api/users/1",
        json={"email": "updated@example.com", "password": "newpasssss"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"

def test_update_user_not_found(client):
    response = client.put(
        "/api/users/999",
        json={"email": "x@x.com", "password": "passfghjkjhg"},
    )
    assert response.status_code == 404


# ───────────────────────────────────────────────
# DELETE /api/users/{user_id}
# ───────────────────────────────────────────────

def test_delete_user_unauthenticated(client):
    response = client.delete("/api/users/1")
    assert response.status_code == 401

def test_delete_user_forbidden(auth_client):
    # Connecté mais pas admin
    response = auth_client.delete("/api/users/1")
    assert response.status_code == 403

def test_delete_user_success(admin_client):
    response = admin_client.delete("/api/users/1")
    assert response.status_code == 204

def test_delete_user_not_found(admin_client):
    response = admin_client.delete("/api/users/999")
    assert response.status_code == 404