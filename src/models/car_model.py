from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config.database import Base

if TYPE_CHECKING:
    from .case_management_model import CaseManagement

class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[int] = mapped_column(Integer)
    km: Mapped[int] = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String(50))
    trade: Mapped[str] = mapped_column(String(50))

    cases: Mapped[list["CaseManagement"]] = relationship(
        "CaseManagement",
        back_populates="car"
    )