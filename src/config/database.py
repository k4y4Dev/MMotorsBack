from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings

#SQLALCHEMY_DATABASE_URL = "sqlite:///./mmotors.db"

#if psycopg3 psycopg[binary] --> new
SQLALCHEMY_DATABASE_URL = settings.connection_string

#if psycopg2
#pip uninstall psycopg psycopg-binary
#pip install psycopg2-binary
#SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:test123@127.0.0.1:5432/mmotors'



engine = create_engine(
    SQLALCHEMY_DATABASE_URL
#    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db