"""FastAPI dependencies for subscription feature gates and token consumption."""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..db.models import User
from ..subscription.constants import PLAN_FEATURES, TOKEN_COSTS
from ..subscription.service import check_feature_access, check_tokens, consume_tokens
from .dependencies import get_current_user


def require_feature(feature: str) -> Callable:
    """Dependency factory: raises 403 if user's plan lacks the feature."""

    async def _check(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        has_access = await check_feature_access(user, feature, db)
        if not has_access:
            required_plan = "basic" if feature == "career" else "premium"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "feature_locked",
                    "feature": feature,
                    "required_plan": required_plan,
                    "upgrade_url": "/pricing",
                    "message": f"此功能需要{_plan_display(required_plan)}才能使用",
                },
            )

    return _check


def require_tokens(action: str) -> Callable:
    """Dependency factory: checks balance and deducts tokens, raises 402 if insufficient."""

    async def _check(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        result = await check_tokens(user, action, db)
        if not result["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "insufficient_tokens",
                    "action": action,
                    "required": result["cost"],
                    "balance": result["balance"],
                    "upgrade_url": "/pricing",
                    "message": f"星辰代幣不足：需要 {result['cost']}，剩餘 {result['balance']}",
                },
            )
        await consume_tokens(user, action, db)

    return _check


def _plan_display(name: str) -> str:
    return {"free": "免費方案", "basic": "基本方案", "premium": "高級方案"}.get(name, name)
