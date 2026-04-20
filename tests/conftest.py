import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool,create_engine
from sqlalchemy.orm import sessionmaker
from src.config.database  import get_db, Base
from main import app
from .entity_test import MockBase, MockSchema



DATABASE_URL="sqlite:///:memory:"

engine =  create_engine(DATABASE_URL,
                        connect_args={
                            "check_same_thread":False,
                        },
                        poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
@pytest.fixture(autouse=True)
def setup_database():
    # Crée les tables avant le test
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    test_item = MockBase(id=50, name="Test", price=365)
    session.add(test_item)
    session.commit()
    session.close()
    yield
    # Supprime les tables après le test
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db= TestingSessionLocal()
    yield db
    db.close()
    
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)