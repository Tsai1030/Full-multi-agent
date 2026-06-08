"""
ORM Models — 使用者帳號、命盤 profile、與大師對談紀錄、訂閱方案、代幣系統

關聯：User 1—N ChartProfile 1—N ChatSession 1—N ChatMessage
      User 1—1 UserSubscription, User 1—1 TokenBalance, User 1—N TokenTransaction
皆用 UUID 主鍵、server_default 時間戳、FK cascade，利於維護。
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
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
    subscription_plan: Mapped[str] = mapped_column(String(20), server_default="free", nullable=False)

    profiles: Mapped[list["ChartProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    subscription: Mapped["UserSubscription | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    token_balance: Mapped["TokenBalance | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
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


# ─── Subscription & Token Models ──────────────────────────────────────────────


class SubscriptionPlan(TimestampMixin, Base):
    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    price_twd: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    max_profiles: Mapped[int] = mapped_column(Integer, nullable=False)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)


class UserSubscription(TimestampMixin, Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscription_plans.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), server_default="active", nullable=False)
    payment_provider: Mapped[str] = mapped_column(String(20), server_default="manual", nullable=False)
    provider_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)

    user: Mapped["User"] = relationship(back_populates="subscription")
    plan: Mapped["SubscriptionPlan"] = relationship()


class TokenBalance(TimestampMixin, Base):
    __tablename__ = "token_balances"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    balance: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="token_balance")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PaymentRecord(TimestampMixin, Base):
    __tablename__ = "payment_records"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_subscriptions.id"), nullable=True
    )
    payment_provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_transaction_id: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_twd: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), server_default="pending", nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
