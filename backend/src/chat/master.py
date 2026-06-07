"""
與大師對談的 LLM 服務

以使用者該命盤 profile 為依據，帶入歷史對話，用算命大師 persona 產生回覆。
提供一次性回覆與逐字串流（SSE）兩種。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from loguru import logger

from ..prompts.master_prompt import MASTER_PERSONA
from ..utils.llm import content_to_text, get_gemini
from ..ziwei import format_chart_for_llm

# 帶入對談的最近歷史則數（避免 context 過長）
_HISTORY_LIMIT = 20


def _build_system_prompt(chart: dict[str, Any]) -> str:
    chart_text = format_chart_for_llm(chart)
    return f"{MASTER_PERSONA}\n\n=== 此人的命盤（你唯一的依據）===\n{chart_text}"


def _build_messages(
    chart: dict[str, Any], history: list[dict[str, str]], user_message: str
) -> list[Any]:
    messages: list[Any] = [SystemMessage(content=_build_system_prompt(chart))]
    for m in history[-_HISTORY_LIMIT:]:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    messages.append(HumanMessage(content=user_message))
    return messages


async def generate_master_reply(
    chart: dict[str, Any], history: list[dict[str, str]], user_message: str
) -> str:
    """一次性回覆（非串流）。"""
    messages = _build_messages(chart, history, user_message)
    resp = await get_gemini().ainvoke(messages)
    reply = content_to_text(resp.content).strip()
    logger.info(f"[master] reply generated ({len(reply)} chars)")
    return reply or "（大師沉吟片刻，請再問一次。）"


async def stream_master_reply(
    chart: dict[str, Any], history: list[dict[str, str]], user_message: str
) -> AsyncIterator[str]:
    """
    逐字串流回覆。Gemini 以 chunk 一段一段回傳，
    每個 chunk 取出純文字部分（過濾 thinking 分段）後逐段 yield。
    """
    messages = _build_messages(chart, history, user_message)
    async for chunk in get_gemini().astream(messages):
        delta = content_to_text(chunk.content)
        if delta:
            yield delta
