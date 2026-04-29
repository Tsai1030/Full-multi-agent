"""
Graph State 定義
LangGraph 各節點共享的狀態結構
"""

from __future__ import annotations

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

    # ── 工具執行結果 ───────────────────────────────────────────
    chart_data: dict[str, Any] | None          # MCP ziwei_chart 結果
    rag_results: list[dict[str, Any]]          # RAG 搜索結果
    search_results: list[dict[str, Any]]       # Web search 結果

    # ── 流程控制 ───────────────────────────────────────────────
    iterations: int                            # 當前迭代次數
    max_iterations: int                        # 最大迭代次數
    should_end: bool                           # 是否結束 loop

    # ── 最終輸出 ───────────────────────────────────────────────
    final_answer: str | None
