from typing import Optional
from src.config.database  import get_db, Base
from sqlalchemy.orm import Session, declarative_base, Mapped, mapped_column
from pydantic import BaseModel


class MockBase(Base):
    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()

class MockSchema(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None