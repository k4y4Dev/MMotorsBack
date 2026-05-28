import os
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings

APP_ENV = os.getenv("APP_ENV", "development")

if APP_ENV == "test":
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    SQLALCHEMY_DATABASE_URL = settings.connection_string
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db