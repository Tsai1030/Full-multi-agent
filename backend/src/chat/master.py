"""
與大師對談的 LLM 服務

以使用者該命盤 profile 為依據，帶入歷史對話，用算命大師 persona 產生回覆。
"""

from __future__ import annotations

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


async def generate_master_reply(
    chart: dict[str, Any],
    history: list[dict[str, str]],
    user_message: str,
) -> str:
    """
    Args:
        chart: 命盤 JSON
        history: 既有對話 [{role: 'user'|'master', content: str}, ...]（不含本次提問）
        user_message: 使用者本次提問
    Returns:
        大師的回覆文字
    """
    messages: list[Any] = [SystemMessage(content=_build_system_prompt(chart))]
    for m in history[-_HISTORY_LIMIT:]:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    messages.append(HumanMessage(content=user_message))

    llm = get_gemini()
    resp = await llm.ainvoke(messages)
    reply = content_to_text(resp.content).strip()
    logger.info(f"[master] reply generated ({len(reply)} chars)")
    return reply or "（大師沉吟片刻，請再問一次。）"
