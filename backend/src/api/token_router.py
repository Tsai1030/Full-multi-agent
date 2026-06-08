"""Token balance and transaction history — /api/tokens"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..db import get_db
from ..db.models import TokenBalance, TokenTransaction, User
from ..subscription.service import check_tokens
from .models import (
    TokenBalanceResponse,
    TokenCheckRequest,
    TokenCheckResponse,
    TokenTransactionResponse,
)

token_router = APIRouter(prefix="/api/tokens", tags=["tokens"])


@token_router.get("/balance", response_model=TokenBalanceResponse)
async def get_balance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TokenBalanceResponse:
    stmt = select(TokenBalance).where(TokenBalance.user_id == user.id)
    bal = await db.scalar(stmt)
    if bal is None:
        return TokenBalanceResponse(balance=0, period_start=None, period_end=None)
    return TokenBalanceResponse(
        balance=bal.balance,
        period_start=bal.period_start.isoformat(),
        period_end=bal.period_end.isoformat(),
    )


@token_router.get("/history", response_model=list[TokenTransactionResponse])
async def get_history(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TokenTransactionResponse]:
    offset = (max(1, page) - 1) * page_size
    stmt = (
        select(TokenTransaction)
        .where(TokenTransaction.user_id == user.id)
        .order_by(TokenTransaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = await db.scalars(stmt)
    return [
        TokenTransactionResponse(
            id=str(tx.id),
            amount=tx.amount,
            action=tx.action,
            reference_id=tx.reference_id,
            balance_after=tx.balance_after,
            created_at=tx.created_at,
        )
        for tx in rows
    ]


@token_router.post("/check", response_model=TokenCheckResponse)
async def check_action(
    req: TokenCheckRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TokenCheckResponse:
    result = await check_tokens(user, req.action, db)
    return TokenCheckResponse(**result)
