from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config.database import Base

if TYPE_CHECKING:
    from .user_model import User
    from .car_model import Car

class CaseManagement(Base):
    __tablename__ = "case_management"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey("cars.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    user: Mapped["User"] = relationship("User", back_populates="cases")
    car: Mapped["Car"] = relationship("Car", back_populates="cases")