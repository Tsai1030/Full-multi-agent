"""
MCP Bridge Tool - 透過 MCP Client 呼叫 ziwei_chart 工具
LangChain @tool 裝飾器，供 LangGraph ToolNode 使用
"""

from __future__ import annotations

import json

from langchain_core.tools import tool
from loguru import logger


@tool
async def get_ziwei_chart(
    gender: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: str,
) -> str:
    """
    呼叫紫微斗數命盤工具，根據出生資料取得完整命盤。
    這是取得紫微斗數命盤的必要第一步。

    Args:
        gender     : 性別（男/女）
        birth_year : 出生年份（西元，例如 1990）
        birth_month: 出生月份（1-12）
        birth_day  : 出生日期（1-31）
        birth_hour : 出生時辰（子/丑/寅/卯/辰/巳/午/未/申/酉/戌/亥）

    Returns:
        命盤資料（JSON 字串），含各宮位星曜
    """
    from ..config.settings import get_settings
    from ..mcp.client import MCPClient

    settings = get_settings()

    arguments = {
        "gender": gender,
        "birth_year": birth_year,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "birth_hour": birth_hour,
    }

    try:
        async with MCPClient(settings.mcp_base_url, timeout=settings.mcp_request_timeout) as client:
            result = await client.call("ziwei_chart", arguments)

        if result.success:
            logger.debug(f"ZiweiChart fetched: {birth_year}/{birth_month}/{birth_day} {birth_hour}")
            return json.dumps(result.data, ensure_ascii=False)
        else:
            logger.warning(f"ZiweiChart MCP error: {result.error}")
            return json.dumps({"error": result.error, "success": False}, ensure_ascii=False)

    except Exception as exc:
        logger.error(f"MCP bridge error: {exc}")
        return json.dumps({"error": str(exc), "success": False}, ensure_ascii=False)
