"""
Graph Edges - 條件式路由函式
決定 orchestrator 執行後要去哪個節點
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage

from .state import GraphState


def should_continue(
    state: GraphState,
) -> Literal["tools", "synthesizer"]:
    """
    orchestrator_node 後的路由決策：

    - 若最後一則 AIMessage 含 tool_calls → 繼續執行工具（tools）
    - 若超過最大迭代次數 → 強制進入 synthesizer
    - 否則（LLM 不再呼叫工具）→ synthesizer
    """
    if state["iterations"] >= state["max_iterations"]:
        return "synthesizer"

    messages = state["messages"]
    if not messages:
        return "synthesizer"

    last = messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"

    return "synthesizer"
