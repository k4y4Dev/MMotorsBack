from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./mmotors.db"

#if psycopg3 psycopg[binary] --> new
#SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg://postgres:test123@127.0.0.1:5432/mmotors'

#if psycopg2
#pip uninstall psycopg psycopg-binary
#pip install psycopg2-binary
#SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:test123@127.0.0.1:5432/mmotors'



engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

#engine = create_engine(
#    SQLALCHEMY_DATABASE_URL
#)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db