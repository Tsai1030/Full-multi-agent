"""Subscription plans and user subscription management — /api/subscription"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..config.settings import get_settings
from ..db import get_db
from ..db.models import SubscriptionPlan, TokenBalance, User, UserSubscription
from ..subscription.service import create_free_subscription, get_user_subscription_info
from .models import PlanResponse, SubscribeRequest, SubscriptionInfoResponse

subscription_router = APIRouter(prefix="/api/subscription", tags=["subscription"])


@subscription_router.get("/plans", response_model=list[PlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)) -> list[PlanResponse]:
    stmt = select(SubscriptionPlan).where(SubscriptionPlan.is_active == True).order_by(SubscriptionPlan.price_twd)
    rows = await db.scalars(stmt)
    return [
        PlanResponse(
            id=str(p.id),
            name=p.name,
            display_name=p.display_name,
            price_twd=p.price_twd,
            monthly_tokens=p.monthly_tokens,
            max_profiles=p.max_profiles,
            features=p.features,
        )
        for p in rows
    ]


@subscription_router.get("/me", response_model=SubscriptionInfoResponse)
async def my_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionInfoResponse:
    info = await get_user_subscription_info(user.id, db)
    return SubscriptionInfoResponse(**info)


@subscription_router.post("/subscribe")
async def subscribe(
    req: SubscribeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Initiate a subscription upgrade. Returns a payment URL (ECPay integration placeholder)."""
    if req.plan_name not in ("basic", "premium"):
        raise HTTPException(status_code=400, detail="Invalid plan")

    if user.subscription_plan == req.plan_name:
        raise HTTPException(status_code=400, detail="已經是此方案")

    # TODO: ECPay integration — generate payment URL and redirect
    # For now, return a placeholder indicating payment integration is needed
    return {
        "message": "Payment integration pending",
        "plan": req.plan_name,
        "note": "ECPay 綠界金流整合尚未完成，需要註冊商家帳號後串接",
    }


@subscription_router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(UserSubscription).where(UserSubscription.user_id == user.id)
    sub = await db.scalar(stmt)
    if sub is None:
        raise HTTPException(status_code=404, detail="No active subscription")

    if user.subscription_plan == "free":
        raise HTTPException(status_code=400, detail="免費方案無需取消")

    sub.cancel_at_period_end = True
    await db.commit()

    return {
        "message": "訂閱將在當期結束後取消",
        "period_end": sub.current_period_end.isoformat(),
    }


@subscription_router.post("/admin/upgrade")
async def admin_upgrade(
    email: str = Query(...),
    secret: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """One-time admin endpoint to upgrade a user to permanent premium.
    Secured by JWT_SECRET_KEY as the admin secret."""
    if secret != get_settings().jwt_secret_key:
        raise HTTPException(status_code=403, detail="Invalid secret")

    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name == "premium"))
    if plan is None:
        raise HTTPException(status_code=500, detail="Premium plan not found")

    permanent_end = datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    user.subscription_plan = "premium"

    sub = await db.scalar(select(UserSubscription).where(UserSubscription.user_id == user.id))
    if sub:
        sub.plan_id = plan.id
        sub.status = "active"
        sub.current_period_start = now
        sub.current_period_end = permanent_end
        sub.cancel_at_period_end = False
    else:
        db.add(UserSubscription(
            user_id=user.id, plan_id=plan.id, status="active",
            payment_provider="manual", current_period_start=now, current_period_end=permanent_end,
        ))

    bal = await db.scalar(select(TokenBalance).where(TokenBalance.user_id == user.id))
    if bal:
        bal.balance = -1
        bal.period_start = now
        bal.period_end = permanent_end
    else:
        db.add(TokenBalance(user_id=user.id, balance=-1, period_start=now, period_end=permanent_end))

    await db.commit()
    return {"message": f"{email} upgraded to permanent premium"}
