"""Core subscription and token business logic."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import (
    SubscriptionPlan,
    TokenBalance,
    TokenTransaction,
    User,
    UserSubscription,
)
from .constants import PLAN_FEATURES, PLAN_MONTHLY_TOKENS, TOKEN_COSTS


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _period_end(start: datetime) -> datetime:
    if start.month == 12:
        return start.replace(year=start.year + 1, month=1)
    return start.replace(month=start.month + 1)


async def _get_free_plan(db: AsyncSession) -> SubscriptionPlan:
    stmt = select(SubscriptionPlan).where(SubscriptionPlan.name == "free")
    plan = await db.scalar(stmt)
    if plan is None:
        raise RuntimeError("Free plan not found in subscription_plans table")
    return plan


async def create_free_subscription(user_id: uuid.UUID, db: AsyncSession) -> None:
    """Create a free subscription and initial token balance for a new user."""
    plan = await _get_free_plan(db)
    now = _now()
    end = _period_end(now)

    sub = UserSubscription(
        user_id=user_id,
        plan_id=plan.id,
        status="active",
        payment_provider="manual",
        current_period_start=now,
        current_period_end=end,
    )
    db.add(sub)

    balance = TokenBalance(
        user_id=user_id,
        balance=plan.monthly_tokens,
        period_start=now,
        period_end=end,
    )
    db.add(balance)

    tx = TokenTransaction(
        user_id=user_id,
        amount=plan.monthly_tokens,
        action="monthly_allocation",
        balance_after=plan.monthly_tokens,
    )
    db.add(tx)


async def get_user_subscription_info(user_id: uuid.UUID, db: AsyncSession) -> dict:
    """Get subscription + token balance info for a user."""
    sub_stmt = (
        select(UserSubscription)
        .where(UserSubscription.user_id == user_id)
    )
    sub = await db.scalar(sub_stmt)

    bal_stmt = select(TokenBalance).where(TokenBalance.user_id == user_id)
    bal = await db.scalar(bal_stmt)

    if sub is None:
        return {
            "plan_name": "free",
            "plan_display_name": "免費方案",
            "status": "active",
            "token_balance": bal.balance if bal else 0,
            "period_end": bal.period_end.isoformat() if bal else None,
            "features": PLAN_FEATURES["free"],
            "monthly_tokens": PLAN_MONTHLY_TOKENS["free"],
            "max_profiles": 2,
            "price_twd": 0,
            "cancel_at_period_end": False,
        }

    plan = await db.get(SubscriptionPlan, sub.plan_id)
    return {
        "plan_name": plan.name if plan else "free",
        "plan_display_name": plan.display_name if plan else "免費方案",
        "status": sub.status,
        "token_balance": bal.balance if bal else 0,
        "period_end": sub.current_period_end.isoformat(),
        "features": plan.features if plan else PLAN_FEATURES["free"],
        "monthly_tokens": plan.monthly_tokens if plan else 5,
        "max_profiles": plan.max_profiles if plan else 2,
        "price_twd": plan.price_twd if plan else 0,
        "cancel_at_period_end": sub.cancel_at_period_end,
    }


async def check_feature_access(user: User, feature: str, db: AsyncSession) -> bool:
    """Check if user's plan grants access to a feature."""
    plan_name = user.subscription_plan
    if plan_name == "premium":
        return True
    features = PLAN_FEATURES.get(plan_name, PLAN_FEATURES["free"])
    return features.get(feature, False)


async def check_tokens(user: User, action: str, db: AsyncSession) -> dict:
    """Check if user can afford an action. Returns {allowed, cost, balance}."""
    if user.subscription_plan == "premium":
        return {"allowed": True, "cost": 0, "balance": -1}

    cost = TOKEN_COSTS.get(action, 0)
    bal_stmt = select(TokenBalance).where(TokenBalance.user_id == user.id)
    bal = await db.scalar(bal_stmt)
    balance = bal.balance if bal else 0

    return {
        "allowed": balance >= cost,
        "cost": cost,
        "balance": balance,
    }


async def consume_tokens(
    user: User,
    action: str,
    db: AsyncSession,
    reference_id: str | None = None,
) -> int:
    """Deduct tokens for an action. Returns new balance. Raises ValueError if insufficient."""
    if user.subscription_plan == "premium":
        return -1

    cost = TOKEN_COSTS.get(action, 0)
    if cost == 0:
        return 0

    bal_stmt = select(TokenBalance).where(TokenBalance.user_id == user.id)
    bal = await db.scalar(bal_stmt)
    if bal is None:
        raise ValueError("Token balance not found")

    if bal.balance < cost:
        raise ValueError(f"Insufficient tokens: need {cost}, have {bal.balance}")

    bal.balance -= cost
    new_balance = bal.balance

    tx = TokenTransaction(
        user_id=user.id,
        amount=-cost,
        action=action,
        reference_id=reference_id,
        balance_after=new_balance,
    )
    db.add(tx)

    return new_balance


async def allocate_monthly_tokens(
    user_id: uuid.UUID, plan_name: str, db: AsyncSession
) -> int:
    """Allocate monthly tokens on billing cycle renewal. Returns new balance."""
    tokens = PLAN_MONTHLY_TOKENS.get(plan_name, 5)
    if tokens == -1:
        return -1

    now = _now()
    end = _period_end(now)

    bal_stmt = select(TokenBalance).where(TokenBalance.user_id == user_id)
    bal = await db.scalar(bal_stmt)

    if bal is None:
        bal = TokenBalance(
            user_id=user_id,
            balance=tokens,
            period_start=now,
            period_end=end,
        )
        db.add(bal)
    else:
        bal.balance = tokens
        bal.period_start = now
        bal.period_end = end

    tx = TokenTransaction(
        user_id=user_id,
        amount=tokens,
        action="monthly_allocation",
        balance_after=tokens,
    )
    db.add(tx)

    return tokens
