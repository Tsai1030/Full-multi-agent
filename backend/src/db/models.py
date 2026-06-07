"""
ORM Models — 使用者帳號、命盤 profile、與大師對談紀錄

關聯：User 1—N ChartProfile 1—N ChatSession 1—N ChatMessage
皆用 UUID 主鍵、server_default 時間戳、FK cascade，利於維護。
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    profiles: Mapped[list["ChartProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ChartProfile(TimestampMixin, Base):
    """使用者儲存的命盤（可多個：自己 / 家人 / 朋友）"""

    __tablename__ = "chart_profiles"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    label: Mapped[str] = mapped_column(String(100), nullable=False)        # 例：我的命盤
    relation: Mapped[str] = mapped_column(String(20), default="self", nullable=False)  # self/family/friend

    gender: Mapped[str] = mapped_column(String(2), nullable=False)
    calendar: Mapped[str] = mapped_column(String(10), default="solar", nullable=False)
    birth_year: Mapped[int] = mapped_column(nullable=False)
    birth_month: Mapped[int] = mapped_column(nullable=False)
    birth_day: Mapped[int] = mapped_column(nullable=False)
    birth_hour: Mapped[str] = mapped_column(String(2), nullable=False)     # 地支

    chart_json: Mapped[dict] = mapped_column(JSONB, nullable=False)        # iztro 命盤

    user: Mapped["User"] = relationship(back_populates="profiles")
    sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class ChatSession(TimestampMixin, Base):
    """一段與大師的對談（綁定某個命盤 profile）"""

    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chart_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), default="與大師對談", nullable=False)

    profile: Mapped["ChartProfile"] = relationship(back_populates="sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    """對談中的單則訊息（role = user / master）"""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False)  # user / master
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
