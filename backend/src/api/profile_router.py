"""
命盤 Profile Router — /api/profiles
使用者儲存 / 列出 / 讀取 / 刪除自己的命盤（可多個）。全部需登入並以 user 範圍過濾。
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..auth.permissions import require_tokens
from ..db import get_db
from ..db.models import ChartProfile, User
from ..subscription.service import get_user_subscription_info
from .models import ProfileCreate, ProfileResponse

profile_router = APIRouter(prefix="/api/profiles", tags=["profiles"])


def _to_response(p: ChartProfile) -> ProfileResponse:
    return ProfileResponse(
        id=str(p.id),
        label=p.label,
        relation=p.relation,
        gender=p.gender,
        birth_year=p.birth_year,
        birth_month=p.birth_month,
        birth_day=p.birth_day,
        birth_hour=p.birth_hour,
        chart=p.chart_json,
        created_at=p.created_at,
    )


async def _get_owned_profile(profile_id: str, user: User, db: AsyncSession) -> ChartProfile:
    try:
        pid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="命盤不存在")
    profile = await db.get(ChartProfile, pid)
    if profile is None or profile.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="命盤不存在")
    return profile


@profile_router.get("", response_model=list[ProfileResponse])
async def list_profiles(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ProfileResponse]:
    rows = await db.scalars(
        select(ChartProfile).where(ChartProfile.user_id == user.id).order_by(ChartProfile.created_at.desc())
    )
    return [_to_response(p) for p in rows]


@profile_router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    req: ProfileCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _tokens: None = Depends(require_tokens("profile_create")),
) -> ProfileResponse:
    info = await get_user_subscription_info(user.id, db)
    if info["max_profiles"] != -1:
        count_stmt = select(ChartProfile.id).where(ChartProfile.user_id == user.id)
        existing = len((await db.scalars(count_stmt)).all())
        if existing >= info["max_profiles"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "profile_limit",
                    "max_profiles": info["max_profiles"],
                    "current": existing,
                    "upgrade_url": "/pricing",
                    "message": f"目前方案最多可儲存 {info['max_profiles']} 個命盤",
                },
            )
    b = req.birth_data
    profile = ChartProfile(
        user_id=user.id,
        label=req.label,
        relation=req.relation,
        gender=b.gender,
        birth_year=b.birth_year,
        birth_month=b.birth_month,
        birth_day=b.birth_day,
        birth_hour=b.birth_hour,
        chart_json=req.chart,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return _to_response(profile)


@profile_router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    return _to_response(await _get_owned_profile(profile_id, user, db))


@profile_router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    profile = await _get_owned_profile(profile_id, user, db)
    await db.delete(profile)
    await db.commit()
