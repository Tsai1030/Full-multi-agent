"""SQLAlchemy DeclarativeBase（所有 ORM model 的共同基底）"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM 宣告基底；Alembic 以 Base.metadata 產生 migration。"""
