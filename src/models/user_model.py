from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config.database import Base

if TYPE_CHECKING:
    from .case_management_model import CaseManagement

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hashed: Mapped[str] = mapped_column(String(200), nullable=False)
    lastname: Mapped[str] = mapped_column(String(200), nullable=False)
    firstname: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)

    cases: Mapped[list["CaseManagement"]] = relationship(
        "CaseManagement",
        back_populates="user"
    )