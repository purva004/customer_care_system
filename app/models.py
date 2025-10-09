from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    neutral = "neutral"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    gender: Mapped[str] = mapped_column(String(16), default=GenderEnum.neutral.value)
    language_code: Mapped[str] = mapped_column(String(16), default="en-US")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic schemas
class CustomerCreate(BaseModel):
    phone_number: str
    name: str | None = None
    gender: GenderEnum | None = None
    language_code: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    gender: GenderEnum | None = None
    language_code: str | None = None


class CustomerOut(BaseModel):
    id: int
    phone_number: str
    name: str | None
    gender: GenderEnum
    language_code: str

    class Config:
        from_attributes = True

