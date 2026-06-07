"""密碼雜湊與 JWT 簽發 / 驗證"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from ..config.settings import get_settings

# bcrypt 上限 72 bytes，超過需先截斷（標準做法）
_BCRYPT_MAX_BYTES = 72


def _to_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(password), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _create_token(subject: str, token_type: str, expires: timedelta) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires,
    }
    return jwt.encode(payload, s.jwt_secret_key, algorithm=s.jwt_algorithm)


def create_access_token(subject: str) -> str:
    s = get_settings()
    return _create_token(subject, "access", timedelta(minutes=s.access_token_expire_minutes))


def create_refresh_token(subject: str) -> str:
    s = get_settings()
    return _create_token(subject, "refresh", timedelta(days=s.refresh_token_expire_days))


def decode_token(token: str, *, expected_type: str | None = None) -> dict[str, Any]:
    """解碼並驗證 JWT；型別不符或過期會丟 jwt 例外。"""
    s = get_settings()
    payload = jwt.decode(token, s.jwt_secret_key, algorithms=[s.jwt_algorithm])
    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"expected {expected_type} token, got {payload.get('type')}")
    return payload
