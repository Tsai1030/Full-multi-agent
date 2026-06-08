"""
Ephemeral fortune follow-up chat — no DB persistence.

Uses the analysis result as context instead of raw chart data.
Frontend maintains conversation state; backend is stateless per request.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from loguru import logger

from ..prompts.fortune_prompt import build_fortune_system_prompt
from ..utils.llm import content_to_text, get_gemini

_HISTORY_LIMIT = 20


def _build_messages(
    domain: str,
    analysis_context: str,
    chart_text: str,
    history: list[dict[str, str]],
    user_message: str,
) -> list:
    system = build_fortune_system_prompt(domain, analysis_context, chart_text)
    messages: list = [SystemMessage(content=system)]
    for m in history[-_HISTORY_LIMIT:]:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    messages.append(HumanMessage(content=user_message))
    return messages


async def stream_fortune_reply(
    domain: str,
    analysis_context: str,
    chart_text: str,
    history: list[dict[str, str]],
    user_message: str,
) -> AsyncIterator[str]:
    messages = _build_messages(domain, analysis_context, chart_text, history, user_message)
    async for chunk in get_gemini().astream(messages):
        delta = content_to_text(chunk.content)
        if delta:
            yield delta
