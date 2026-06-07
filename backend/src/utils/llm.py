"""共用 Gemini LLM 工具（graph 與 chat 共用）"""

from __future__ import annotations

from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI


def get_gemini() -> ChatGoogleGenerativeAI:
    from ..config.settings import get_settings

    s = get_settings()
    return ChatGoogleGenerativeAI(
        model=s.gemini_model,
        google_api_key=s.google_api_key,
        max_output_tokens=s.gemini_max_tokens,
        temperature=s.gemini_temperature,
    )


def content_to_text(content: Any) -> str:
    """把 LLM 回覆統一轉純文字（Gemini 3.x 可能回 list of parts）。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict) and p.get("type") in (None, "text") and p.get("text"):
                parts.append(str(p["text"]))
        return "".join(parts)
    return str(content) if content is not None else ""
