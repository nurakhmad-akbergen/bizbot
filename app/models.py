import datetime as dt
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        default=lambda: dt.datetime.utcnow(),
        nullable=False
    )

    users = relationship("User", back_populates="business")
    records = relationship("Record", back_populates="business")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False
    )

    # WhatsApp chatId из Green API обычно выглядит как "7707xxxxxxx@c.us"
    chat_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )

    # owner / manager
    role: Mapped[str] = mapped_column(
        String(20),
        default="manager",
        nullable=False
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        default=lambda: dt.datetime.utcnow(),
        nullable=False
    )

    business = relationship("Business", back_populates="users")
    records = relationship("Record", back_populates="user")


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    # sale / expense / stock_in / adjust
    type: Mapped[str] = mapped_column(String(20), nullable=False)

    # когда сообщение пришло (аудит)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        default=lambda: dt.datetime.utcnow(),
        nullable=False
    )

    # когда реально произошло (из текста или из timestamp сообщения)
    occurred_at: Mapped[dt.datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    item_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    qty: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 3),
        nullable=True
    )

    unit_price: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2),
        nullable=True
    )

    amount: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2),
        nullable=True
    )

    currency: Mapped[str] = mapped_column(
        String(8),
        default="KZT",
        nullable=False
    )

    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # кастомные поля под бизнес: {"client":"...", "shift":"..."}
    extra: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False
    )

    business = relationship("Business", back_populates="records")
    user = relationship("User", back_populates="records")