"""
API Request / Response 模型
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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


class AnalysisResponse(BaseModel):
    success: bool
    result: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SystemStatusResponse(BaseModel):
    status: str
    rag_docs: int
    tools: list[str]
    graph_nodes: list[str]
