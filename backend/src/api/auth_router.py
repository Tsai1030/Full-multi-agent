"""
認證 Router — /api/auth
register / login / refresh / logout / me

access token 走 JSON 回傳（前端存記憶體）；
refresh token 走 httpOnly cookie（前端不可讀，自動隨請求帶上）。
"""

from __future__ import annotations

import uuid

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..config.settings import get_settings
from ..db import get_db
from ..db.models import ChartProfile, User
from ..subscription.service import create_free_subscription
from .models import (
    GoogleAuthRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=str(user.id), email=user.email, display_name=user.display_name)


def _set_refresh_cookie(response: Response, user_id: str) -> None:
    s = get_settings()
    response.set_cookie(
        key=s.refresh_cookie_name,
        value=create_refresh_token(user_id),
        httponly=True,
        secure=s.cookie_secure,
        samesite=s.cookie_samesite,
        max_age=s.refresh_token_expire_days * 24 * 3600,
        path="/api/auth",
    )


async def _has_profile(user: User, db: AsyncSession) -> bool:
    return await db.scalar(
        select(ChartProfile.id).where(ChartProfile.user_id == user.id).limit(1)
    ) is not None


def _issue_tokens(response: Response, user: User, *, has_profile: bool = True) -> TokenResponse:
    _set_refresh_cookie(response, str(user.id))
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        user=_user_response(user),
        has_profile=has_profile,
    )


@auth_router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await db.scalar(select(User).where(User.email == req.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="此 Email 已被註冊")

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.display_name,
    )
    db.add(user)
    await db.flush()  # 取得 user.id 後一併建立主命盤

    b = req.birth_data
    db.add(
        ChartProfile(
            user_id=user.id,
            label="我的命盤",
            relation="self",
            gender=b.gender,
            birth_year=b.birth_year,
            birth_month=b.birth_month,
            birth_day=b.birth_day,
            birth_hour=b.birth_hour,
            chart_json=req.chart,
        )
    )
    await db.flush()
    await create_free_subscription(user.id, db)

    await db.commit()
    await db.refresh(user)
    logger.info(f"User registered with primary chart: {user.email}")
    return _issue_tokens(response, user, has_profile=True)


@auth_router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == req.email))
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email 或密碼錯誤")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="帳號已停用")
    return _issue_tokens(response, user, has_profile=await _has_profile(user, db))


@auth_router.post("/google", response_model=TokenResponse)
async def google_auth(req: GoogleAuthRequest, response: Response, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    s = get_settings()
    if not s.google_oauth_client_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="尚未設定 Google 登入")

    from google.auth.transport import requests as g_requests
    from google.oauth2 import id_token as g_id_token

    try:
        info = g_id_token.verify_oauth2_token(req.credential, g_requests.Request(), s.google_oauth_client_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google 憑證無效")

    email = info.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google 帳號缺少 Email")

    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        # Google 使用者無密碼，給一組無法用於密碼登入的隨機 hash
        import secrets

        user = User(
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            display_name=info.get("name") or email.split("@")[0],
        )
        db.add(user)
        await db.flush()
        await create_free_subscription(user.id, db)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User created via Google: {email}")

    return _issue_tokens(response, user, has_profile=await _has_profile(user, db))


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=get_settings().refresh_cookie_name),
) -> TokenResponse:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少 refresh token")
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token 無效或過期")

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="使用者不存在")
    return _issue_tokens(response, user)  # 輪替 refresh + 發新 access


@auth_router.post("/logout")
async def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(get_settings().refresh_cookie_name, path="/api/auth")
    return {"success": True}


@auth_router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return _user_response(user)
