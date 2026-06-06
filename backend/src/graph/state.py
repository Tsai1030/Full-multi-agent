"""
Graph State 定義
LangGraph 各節點共享的狀態結構
"""

from __future__ import annotations

import operator
from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    紫微斗數 Multi-Agent Graph 的全局狀態

    所有節點讀取同一份 state，透過 return dict 更新各自負責的欄位。
    messages 欄位使用 add_messages reducer（自動 append，不覆蓋）。
    """

    # ── 對話歷史（LangGraph 標準 reducer）──────────────────────
    messages: Annotated[list[BaseMessage], add_messages]

    # ── 使用者輸入 ─────────────────────────────────────────────
    birth_data: dict[str, Any]       # gender, birth_year, birth_month, birth_day, birth_hour
    domain_type: str                  # love / wealth / future / comprehensive
    user_question: str                # 使用者的具體問題

    # ── 命盤資料（前端 iztro 計算後送入）──────────────────────
    chart_data: dict[str, Any] | None

    # ── researcher 產出的共享知識脈絡（RAG）────────────────────
    rag_context: str

    # ── 多代理人各自的分析輸出 ─────────────────────────────────
    # 三個並行 agent 各自 append 一筆 {role, label, content}，
    # 用 operator.add reducer 合併（並行寫入不衝突）。
    agent_outputs: Annotated[list[dict[str, Any]], operator.add]

    # ── 既有欄位（保留向後相容，部分已不再使用）────────────────
    rag_results: list[dict[str, Any]]
    search_results: list[dict[str, Any]]
    iterations: int
    max_iterations: int
    should_end: bool

    # ── 最終輸出（coordinator 整合後報告）──────────────────────
    final_answer: str | None
