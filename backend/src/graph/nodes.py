"""
Graph Nodes
每個節點是一個純函式（async），接收 GraphState 並回傳 state 更新 dict。

節點職責：
  orchestrator  - 決定下一步行動（呼叫哪個工具 or 結束）
  tool_executor - 執行 LangGraph ToolNode 的工具
  synthesizer   - 彙整所有資訊，生成最終命盤解析
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from loguru import logger

from .state import GraphState
from ..tools import search_ziwei_knowledge, web_search
from ..ziwei import format_chart_for_llm

# ── 工具清單（供 ToolNode 與 LLM 使用）────────────────────────
# 命盤已由前端 iztro 計算並隨請求送入 state，故不再需要取盤工具，
# orchestrator 只需查詢知識庫 / 網路補充資訊。
AGENT_TOOLS = [search_ziwei_knowledge, web_search]


def _get_llm(with_tools: bool = True) -> ChatGoogleGenerativeAI:
    from ..config.settings import get_settings
    s = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=s.gemini_model,
        google_api_key=s.google_api_key,
        max_output_tokens=s.gemini_max_tokens,
        temperature=s.gemini_temperature,
    )
    return llm.bind_tools(AGENT_TOOLS) if with_tools else llm


# ── Orchestrator Node ─────────────────────────────────────────

ORCHESTRATOR_SYSTEM = """\
你是一個紫微斗數命理分析系統的 AI 協調者。

命盤已由系統（iztro 排盤引擎）精準計算完成，並附在使用者訊息中，
你不需要、也不應該自行排盤或編造星曜，請完全以附上的命盤為準。

你擁有以下工具：
1. search_ziwei_knowledge - 搜索紫微斗數知識庫（RAG）
2. web_search             - 搜索網路上的最新資訊

分析流程：
1. 先閱讀附上的命盤，找出命宮主星、身宮、五行局與請求領域相關的宮位
2. 用 search_ziwei_knowledge 查詢命盤中主要星曜 / 宮位 / 四化的涵義
3. 視需要用 web_search 補充運勢資訊
4. 當你蒐集到足夠資訊後，回覆「分析完成，我已準備好撰寫最終報告。」

重要：每次只呼叫一個工具，蒐集到足夠資訊後才停止工具呼叫。
"""


async def orchestrator_node(state: GraphState) -> dict[str, Any]:
    """
    主控節點：使用 LLM 決定下一步要呼叫哪個工具。
    當 LLM 認為資料充足時停止呼叫工具（不再帶 tool_calls）。

    注意：首次進入時必須把使用者訊息（含命盤）持久化進 state，
    否則之後的回合會以「model function_call」開頭，
    Gemini 會拒絕（function call 必須緊接在 user / function_response 之後）。
    """
    logger.info(f"[orchestrator] iteration={state['iterations']}")

    history = list(state["messages"])
    new_messages: list[BaseMessage] = []

    # 首次進入：建構並持久化使用者訊息（含命盤）
    if not history:
        birth = state["birth_data"]
        chart_text = format_chart_for_llm(state.get("chart_data"))
        intro = (
            f"請分析此命盤：\n"
            f"- 性別：{birth.get('gender')}\n"
            f"- 出生：{birth.get('birth_year')}年{birth.get('birth_month')}月"
            f"{birth.get('birth_day')}日 {birth.get('birth_hour')}時\n"
            f"- 分析領域：{state['domain_type']}\n"
            f"- 問題：{state.get('user_question', '整體命盤解析')}\n\n"
            f"以下是系統排好的命盤，請以此為唯一依據：\n\n"
            f"{chart_text}"
        )
        human = HumanMessage(content=intro)
        new_messages.append(human)
        history = [human]

    llm = _get_llm(with_tools=True)
    # SystemMessage 每次都帶（langchain-google-genai 會轉成 system_instruction，不入歷史）
    response: AIMessage = await llm.ainvoke(
        [SystemMessage(content=ORCHESTRATOR_SYSTEM), *history]
    )
    new_messages.append(response)

    return {
        "messages": new_messages,
        "iterations": state["iterations"] + 1,
    }


# ── ToolNode（LangGraph prebuilt）────────────────────────────

tool_node = ToolNode(AGENT_TOOLS)


# ── Synthesizer Node ──────────────────────────────────────────

SYNTHESIZER_SYSTEM = """\
你是一位專業的紫微斗數命理師，擅長以清晰易懂的方式解析命盤。

請根據以下資料，撰寫一份完整的命盤解析報告：
1. 以繁體中文回覆
2. 先點明命宮主星與格局
3. 針對請求的分析領域深入解析
4. 給出具體的建議
5. 語氣專業但親切，避免絕對化的負面預測

輸出格式：
## 命盤基本格局
## {domain_type} 分析
## 建議與注意事項
"""


async def synthesizer_node(state: GraphState) -> dict[str, Any]:
    """
    彙整節點：整合所有工具結果，生成最終命盤解析報告。
    """
    logger.info("[synthesizer] generating final answer")

    # 整理所有對話歷史成彙整提示
    tool_summary = _build_tool_summary(state)

    domain = state.get("domain_type", "comprehensive")
    system_prompt = SYNTHESIZER_SYSTEM.replace("{domain_type}", domain)

    final_request = (
        f"請根據以下收集到的所有資料，撰寫最終的紫微斗數命盤解析報告。\n\n"
        f"{tool_summary}"
    )

    llm = _get_llm(with_tools=False)
    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"],
        HumanMessage(content=final_request),
    ]
    response: AIMessage = await llm.ainvoke(messages)

    return {
        "final_answer": _content_to_text(response.content),
        "messages": [response],
        "should_end": True,
    }


# ── helpers ───────────────────────────────────────────────────

def _content_to_text(content: Any) -> str:
    """
    把 LLM 回覆內容統一轉成純文字。
    Gemini 3.x（含 thinking）回傳的 content 可能是 list of parts，
    每個 part 為 {'type': 'text', 'text': '...'} 或字串。
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                # 只取文字部分，忽略 thinking signature 等
                if p.get("type") in (None, "text") and p.get("text"):
                    parts.append(str(p["text"]))
        return "".join(parts)
    return str(content) if content is not None else ""


def _build_tool_summary(state: GraphState) -> str:
    """從 messages 中提取工具呼叫結果摘要"""
    from langchain_core.messages import ToolMessage

    parts = []
    for msg in state["messages"]:
        if isinstance(msg, ToolMessage):
            parts.append(f"[工具：{msg.name}]\n{msg.content[:1000]}")
    return "\n\n".join(parts) if parts else "（無工具結果）"
