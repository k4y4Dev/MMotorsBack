import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from src.config.database import get_db, Base
from src.models.user_model import User  # adapte l'import selon ton projet
from src.service.auth_py import get_current_user  # ← la fonction, pas CurrentUser
from main import app
from tests.test_config import TestingSessionLocal, engine, override_get_db
from .entity_test import MockBase, MockSchema, MockDeclarativeBase 

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    MockDeclarativeBase .metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    test_item = MockBase(id=50, name="Test", price=365)
    session.add(test_item)
    session.commit()
    session.close()

    yield
    Base.metadata.drop_all(bind=engine)
    MockDeclarativeBase .metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    """Session ouverte après que setup_database ait créé et peuplé les tables."""
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --- Utilisateur simulé standard ---
def make_mock_user(email: str = "user@example.com", role: str = "user") -> User:
    user = User()
    user.id = 1
    user.email = email
    user.lastname = "Test"
    user.firstname = "Jean"
    user.role = role
    return user


@pytest.fixture
def auth_client(client):
    """Client authentifié en tant qu'utilisateur classique."""
    def mock_current_user():
        return make_mock_user("user@example.com", role="user")  # pas admin → 403 sur create_car

    app.dependency_overrides[get_current_user] = mock_current_user  # ← clé correcte
    yield client
    # le clear() dans `client` s'en charge, mais on peut être explicite :
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def admin_client(client):
    """Client authentifié en tant qu'admin (peut créer/modifier/supprimer)."""
    def mock_admin_user():
        return make_mock_user("admin1@gmail.com", role="admin")  # ← email hardcodé dans ton router

    app.dependency_overrides[get_current_user] = mock_admin_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)