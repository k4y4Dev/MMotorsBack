import pytest
from datetime import timedelta, UTC, datetime
from unittest.mock import MagicMock
from fastapi import HTTPException
import jwt

from src.service.auth_py import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    get_current_user,
)
from config import settings


# ───────────────────────────────────────────────
# hash_password / verify_password
# ───────────────────────────────────────────────

def test_hash_password_returns_hash():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert isinstance(hashed, str)


def test_verify_password_correct():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("secret123")
    assert verify_password("wrongpassword", hashed) is False


# ───────────────────────────────────────────────
# create_access_token
# ───────────────────────────────────────────────

def test_create_access_token_returns_string():
    token = create_access_token({"sub": "42"})
    assert isinstance(token, str)


def test_create_access_token_contains_sub():
    token = create_access_token({"sub": "42"})
    payload = jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.algorithm],
    )
    assert payload["sub"] == "42"


def test_create_access_token_custom_expiry():
    token = create_access_token({"sub": "42"}, expires_delta=timedelta(minutes=1))
    payload = jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.algorithm],
    )
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    # L'expiration doit être dans moins de 2 minutes
    assert exp > datetime.now(UTC)
    assert exp < datetime.now(UTC) + timedelta(minutes=2)


# ───────────────────────────────────────────────
# verify_access_token
# ───────────────────────────────────────────────

def test_verify_access_token_valid():
    token = create_access_token({"sub": "42"})
    result = verify_access_token(token)
    assert result == "42"


def test_verify_access_token_expired():
    token = create_access_token({"sub": "42"}, expires_delta=timedelta(seconds=-1))
    result = verify_access_token(token)
    assert result is None


def test_verify_access_token_invalid_string():
    result = verify_access_token("not.a.valid.token")
    assert result is None


def test_verify_access_token_missing_sub():
    # Token sans "sub" → doit retourner None car "require" exige sub
    token = jwt.encode(
        {"exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    result = verify_access_token(token)
    assert result is None


# ───────────────────────────────────────────────
# get_current_user
# ───────────────────────────────────────────────

def make_mock_request(token: str | None) -> MagicMock:
    """Crée un objet Request simulé avec ou sans cookie auth_token."""
    request = MagicMock()
    request.cookies = {"auth_token": token} if token else {}
    return request


def make_mock_db(user=None) -> MagicMock:
    """Crée une session DB simulée retournant un utilisateur ou None."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = user

    db = MagicMock()
    db.execute.return_value = mock_result
    return db


def make_user(id: int = 1, email: str = "test@example.com"):
    from src.models.user_model import User
    user = User()
    user.id = id
    user.email = email
    return user


def test_get_current_user_no_cookie():
    request = make_mock_request(None)
    db = make_mock_db()

    with pytest.raises(HTTPException) as exc:
        get_current_user(request, db)
    assert exc.value.status_code == 401
    assert "cookie" in exc.value.detail.lower()


def test_get_current_user_invalid_token():
    request = make_mock_request("invalid.token.here")
    db = make_mock_db()

    with pytest.raises(HTTPException) as exc:
        get_current_user(request, db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Unknown ID"


def test_get_current_user_non_integer_sub():
    # sub présent mais non convertible en int
    token = jwt.encode(
        {
            "sub": "not-an-int",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    request = make_mock_request(token)
    db = make_mock_db()

    with pytest.raises(HTTPException) as exc:
        get_current_user(request, db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"


def test_get_current_user_not_found_in_db():
    token = create_access_token({"sub": "99"})
    request = make_mock_request(token)
    db = make_mock_db(user=None)  # ← DB ne trouve personne

    with pytest.raises(HTTPException) as exc:
        get_current_user(request, db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"


def test_get_current_user_success():
    user = make_user(id=1, email="test@example.com")
    token = create_access_token({"sub": "1"})
    request = make_mock_request(token)
    db = make_mock_db(user=user)

    result = get_current_user(request, db)
    assert result.id == 1
    assert result.email == "test@example.com"