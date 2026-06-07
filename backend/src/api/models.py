"""
API Request / Response 模型
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class BirthData(BaseModel):
    gender: str = Field(..., description="性別：男/女")
    birth_year: int = Field(..., ge=1900, le=2100, description="出生年份（西元）")
    birth_month: int = Field(..., ge=1, le=12, description="出生月份")
    birth_day: int = Field(..., ge=1, le=31, description="出生日期")
    birth_hour: str = Field(
        ...,
        description="出生時辰（子/丑/寅/卯/辰/巳/午/未/申/酉/戌/亥）",
    )


class AnalysisRequest(BaseModel):
    birth_data: BirthData
    domain_type: str = Field(
        default="comprehensive",
        description="分析領域：love / wealth / future / comprehensive",
    )
    user_question: str = Field(
        default="",
        description="使用者的具體問題（可選）",
    )
    chart: dict[str, Any] | None = Field(
        default=None,
        description="前端 iztro 計算好的命盤 JSON（命宮、十二宮、星曜、四化…）",
    )


class AgentOutput(BaseModel):
    role: str = Field(..., description="agent 角色代碼：reasoning / domain / creative")
    label: str = Field(..., description="顯示名稱，如「推理分析師」")
    content: str = Field(..., description="該 agent 的個別分析內容")


class AnalysisResponse(BaseModel):
    success: bool
    result: str | None = None
    error: str | None = None
    agents: list[AgentOutput] | None = Field(
        default=None, description="多代理人各自的分析（供前端展示運作過程）"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class SystemStatusResponse(BaseModel):
    status: str
    rag_docs: int
    tools: list[str]
    graph_nodes: list[str]


# ── Auth ───────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=100)
    # 註冊時一併建立帳號主人的主命盤
    birth_data: BirthData
    chart: dict[str, Any] = Field(..., description="前端 iztro 計算好的命盤 JSON")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., description="Google Identity Services 回傳的 ID token")


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    # 是否已有命盤；前端據此決定要不要導去「補生辰」頁
    has_profile: bool = True


# ── Chart Profile ──────────────────────────────────────────────


class ProfileCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=100, description="命盤名稱，如「我的命盤」")
    relation: str = Field("self", description="self / family / friend")
    birth_data: BirthData
    chart: dict[str, Any] = Field(..., description="iztro 命盤 JSON")


class ProfileResponse(BaseModel):
    id: str
    label: str
    relation: str
    gender: str
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: str
    chart: dict[str, Any]
    created_at: datetime


# ── Chat（與大師對談）──────────────────────────────────────────


class ChatSessionCreate(BaseModel):
    profile_id: str
    title: str | None = None


class ChatSessionResponse(BaseModel):
    id: str
    profile_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ChatSendRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
