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

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from loguru import logger

from .state import GraphState
from ..tools import get_ziwei_chart, search_ziwei_knowledge, web_search

# ── 工具清單（供 ToolNode 與 LLM 使用）────────────────────────
AGENT_TOOLS = [get_ziwei_chart, search_ziwei_knowledge, web_search]


def _get_llm(with_tools: bool = True) -> ChatAnthropic:
    from ..config.settings import get_settings
    s = get_settings()
    llm = ChatAnthropic(
        model=s.anthropic_model,
        api_key=s.anthropic_api_key,
        max_tokens=s.anthropic_max_tokens,
        temperature=s.anthropic_temperature,
    )
    return llm.bind_tools(AGENT_TOOLS) if with_tools else llm


# ── Orchestrator Node ─────────────────────────────────────────

ORCHESTRATOR_SYSTEM = """\
你是一個紫微斗數命理分析系統的 AI 協調者。

你擁有以下工具：
1. get_ziwei_chart    - 取得紫微斗數命盤（必須第一步執行）
2. search_ziwei_knowledge - 搜索紫微斗數知識庫（RAG）
3. web_search         - 搜索網路上的最新資訊

分析流程：
1. 先呼叫 get_ziwei_chart 取得命盤
2. 用 search_ziwei_knowledge 查詢命盤中主要星曜的涵義
3. 視需要用 web_search 補充運勢資訊
4. 當你蒐集到足夠資訊後，回覆「分析完成，我已準備好撰寫最終報告。」

重要：每次只呼叫一個工具，蒐集到足夠資訊後才停止工具呼叫。
"""


async def orchestrator_node(state: GraphState) -> dict[str, Any]:
    """
    主控節點：使用 Claude 決定下一步要呼叫哪個工具。
    當 Claude 認為資料充足時停止呼叫工具（不再帶 tool_calls）。
    """
    logger.info(f"[orchestrator] iteration={state['iterations']}")

    # 首次進入，建構初始訊息
    if not state["messages"]:
        birth = state["birth_data"]
        intro = (
            f"請分析此命盤：\n"
            f"- 性別：{birth.get('gender')}\n"
            f"- 出生：{birth.get('birth_year')}年{birth.get('birth_month')}月"
            f"{birth.get('birth_day')}日 {birth.get('birth_hour')}時\n"
            f"- 分析領域：{state['domain_type']}\n"
            f"- 問題：{state.get('user_question', '整體命盤解析')}"
        )
        initial_messages = [
            SystemMessage(content=ORCHESTRATOR_SYSTEM),
            HumanMessage(content=intro),
        ]
    else:
        initial_messages = [SystemMessage(content=ORCHESTRATOR_SYSTEM)]

    llm = _get_llm(with_tools=True)
    messages_to_send = initial_messages if not state["messages"] else state["messages"]
    response: AIMessage = await llm.ainvoke(messages_to_send)

    return {
        "messages": [response],
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
        "final_answer": response.content,
        "messages": [response],
        "should_end": True,
    }


# ── helpers ───────────────────────────────────────────────────

def _build_tool_summary(state: GraphState) -> str:
    """從 messages 中提取工具呼叫結果摘要"""
    from langchain_core.messages import ToolMessage

    parts = []
    for msg in state["messages"]:
        if isinstance(msg, ToolMessage):
            parts.append(f"[工具：{msg.name}]\n{msg.content[:1000]}")
    return "\n\n".join(parts) if parts else "（無工具結果）"
