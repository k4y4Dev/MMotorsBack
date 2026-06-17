from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config.database import Base

if TYPE_CHECKING:
    from .user_model import User

class UserDoc(Base):
    __tablename__ = "user_doc"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(100), nullable=False)
    doc_url: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user: Mapped["User"] = relationship("User", back_populates="doc_list")
